from django.db.models import Avg, Case, Count, F, When
from django.db.models.functions import TruncDate

from ohq.models import Question, QueueStatistic, MembershipStatistic


def calculate_student_avg_time_stats(user, questions, course):
    num_questions = total_time_helped = total_time_waiting = 0
    for question in questions:
        total_time_helped += (question.time_responded_to - question.time_response_started).seconds
        total_time_waiting += (question.time_response_started - question.time_asked).seconds
        num_questions += 1
    
    avg_time_helped = total_time_helped / num_questions
    avg_time_waiting = total_time_waiting / num_questions
    
    MembershipStatistic.objects.update_or_create(
        user=user,
        course=course,
        metric=MembershipStatistic.METRIC_STUDENT_AVG_TIME_HELPED,
        defaults={"value": avg_time_helped}
    )
    
    MembershipStatistic.objects.update_or_create(
        user=user,
        course=course,
        metric=MembershipStatistic.METRIC_STUDENT_AVG_TIME_WAITING,
        defaults={"value": avg_time_waiting}
    )

def calculate_instructor_avg_time_stats(user, questions, course):
    num_questions = total_time = 0
    for question in questions:
        total_time += (question.time_responded_to - question.time_response_started).seconds
        num_questions += 1
    
    avg_time = total_time / num_questions
    questions_per_hour = (num_questions / total_time) * 3600

    METRIC_INSTR_AVG_TIME_HELPING = "INSTR_AVG_TIME_HELPING"
    METRIC_INSTR_AVG_STUDENTS_PER_HOUR = "INSTR_AVG_STUDENTS_PER_HOUR"
    
    MembershipStatistic.objects.update_or_create(
        user=user,
        course=course,
        metric=MembershipStatistic.METRIC_INSTR_AVG_TIME_HELPING,
        defaults={"value": avg_time}
    )
    
    MembershipStatistic.objects.update_or_create(
        user=user,
        course=course,
        metric=MembershipStatistic.METRIC_INSTR_AVG_STUDENTS_PER_HOUR,
        defaults={"value": questions_per_hour}
    )       

def calculate_avg_queue_wait(queue, start_date, end_date):
    avg = Question.objects.filter(
        queue=queue,
        time_asked__date__range=[prev_sunday, coming_sunday],
        time_response_started__isnull=False,
    ).aggregate(avg_wait=Avg(F("time_response_started") - F("time_asked")))

    wait = avg["avg_wait"]

    QueueStatistic.objects.update_or_create(
        queue=queue,
        metric=QueueStatistic.METRIC_AVG_WAIT,
        date=prev_sunday,
        defaults={"value": wait.seconds if wait else 0},
    )


def calculate_avg_time_helping(queue, prev_sunday, coming_sunday):
    avg = Question.objects.filter(
        queue=queue,
        status=Question.STATUS_ANSWERED,
        time_response_started__date__range=[prev_sunday, coming_sunday],
        time_responded_to__isnull=False,
    ).aggregate(avg_time=Avg(F("time_responded_to") - F("time_response_started")))

    duration = avg["avg_time"]

    QueueStatistic.objects.update_or_create(
        queue=queue,
        metric=QueueStatistic.METRIC_AVG_TIME_HELPING,
        date=prev_sunday,
        defaults={"value": duration.seconds if duration else 0},
    )


def calculate_wait_time_heatmap(queue, weekday, hour):
    interval_avg = Question.objects.filter(
        queue=queue,
        time_asked__week_day=weekday,
        time_asked__hour=hour,
        time_response_started__isnull=False,
    ).aggregate(avg_wait=Avg(F("time_response_started") - F("time_asked")))

    interval_avg_wait = interval_avg["avg_wait"]

    QueueStatistic.objects.update_or_create(
        queue=queue,
        metric=QueueStatistic.METRIC_HEATMAP_WAIT,
        day=weekday,
        hour=hour,
        defaults={"value": interval_avg_wait.seconds if interval_avg_wait else 0},
    )


def calculate_num_questions_ans(queue, prev_sunday, coming_saturday):
    num_questions = Question.objects.filter(
        queue=queue,
        status=Question.STATUS_ANSWERED,
        time_responded_to__date__range=[prev_sunday, coming_saturday],
    ).count()

    QueueStatistic.objects.update_or_create(
        queue=queue,
        metric=QueueStatistic.METRIC_NUM_ANSWERED,
        date=prev_sunday,
        defaults={"value": num_questions},
    )


def calculate_num_students_helped(queue, prev_sunday, coming_saturday):
    num_students = (
        Question.objects.filter(
            queue=queue,
            status=Question.STATUS_ANSWERED,
            time_responded_to__date__range=[prev_sunday, coming_saturday],
        )
        .distinct("asked_by")
        .count()
    )

    QueueStatistic.objects.update_or_create(
        queue=queue,
        metric=QueueStatistic.METRIC_STUDENTS_HELPED,
        date=prev_sunday,
        defaults={"value": num_students},
    )


def calculate_questions_per_ta_heatmap(queue, weekday, hour):
    interval_stats = (
        Question.objects.filter(queue=queue, time_asked__week_day=weekday, time_asked__hour=hour)
        .annotate(date=TruncDate("time_asked"))
        .values("date")
        .annotate(
            questions=Count("date", distinct=False), tas=Count("responded_to_by", distinct=True),
        )
        .annotate(
            q_per_ta=Case(When(tas=0, then=F("questions")), default=1.0 * F("questions") / F("tas"))
        )
        .aggregate(avg=Avg(F("q_per_ta")))
    )

    statistic = interval_stats["avg"]

    QueueStatistic.objects.update_or_create(
        queue=queue,
        metric=QueueStatistic.METRIC_HEATMAP_QUESTIONS_PER_TA,
        day=weekday,
        hour=hour,
        defaults={"value": statistic if statistic else 0},
    )
