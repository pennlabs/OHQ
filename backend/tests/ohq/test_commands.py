from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from ohq.models import (
    Course,
    Membership,
    MembershipInvite,
    Question,
    Queue,
    QueueStatistic,
    Semester,
)


User = get_user_model()


@patch("ohq.management.commands.calculatewaittimes.calculate_wait_times")
class CalculateWaitTimesTestCase(TestCase):
    def test_call_command(self, mock_calculate):
        out = StringIO()
        call_command("calculatewaittimes", stdout=out)
        mock_calculate.assert_called()
        self.assertEqual("Updated estimated queue wait times!\n", out.getvalue())


class RegisterClassTestCase(TestCase):
    def setUp(self):
        self.course = ("CIS", "160", "Math", "FALL", "2020")

        Semester.objects.create(year="2020", term="FALL")
        User.objects.create_user("prof1", "prof1@a.com", "prof1")
        User.objects.create_user("head1", "head1@a.com", "head1")

    def test_input_email_role_length_mismatch(self):
        with self.assertRaises(CommandError):
            call_command(
                "createcourse",
                *self.course,
                emails=["a@b.com", "a@c.com"],
                roles=[Membership.KIND_PROFESSOR],
            )

    def test_register_class(self):
        out = StringIO()
        call_command(
            "createcourse",
            *self.course,
            emails=["prof1@a.com", "head1@a.com", "prof2@a.com", "head2@a.com"],
            roles=[
                Membership.KIND_PROFESSOR,
                Membership.KIND_HEAD_TA,
                Membership.KIND_PROFESSOR,
                Membership.KIND_HEAD_TA,
            ],
            stdout=out,
        )
        course = Course.objects.get(department="CIS", course_code="160")
        self.assertEqual(course.course_title, "Math")
        self.assertEqual(course.semester.year, 2020)
        self.assertEqual(course.semester.term, "FALL")

        prof1 = Membership.objects.get(
            course__course_code="160", course__department="CIS", user__email="prof1@a.com"
        )
        prof2 = MembershipInvite.objects.get(
            course__course_code="160", course__department="CIS", email="prof2@a.com"
        )
        head1 = Membership.objects.get(
            course__course_code="160", course__department="CIS", user__email="head1@a.com"
        )
        head2 = MembershipInvite.objects.get(
            course__course_code="160", course__department="CIS", email="head2@a.com"
        )

        self.assertEqual(Membership.KIND_PROFESSOR, prof1.kind)
        self.assertEqual(Membership.KIND_PROFESSOR, prof2.kind)
        self.assertEqual(Membership.KIND_HEAD_TA, head1.kind)
        self.assertEqual(Membership.KIND_HEAD_TA, head2.kind)

        course_msg = "Created new course 'CIS 160: Fall 2020'"
        prof_msg = "Added 1 professor(s) and invited 1 professor(s)"
        ta_msg = "Added 1 Head TA(s) and invited 1 Head TA(s)"

        stdout_msg = course_msg + "\n" + prof_msg + "\n" + ta_msg + "\n"

        self.assertEqual(stdout_msg, out.getvalue())


class AverageQueueWaitTimeTestCase(TestCase):
    def setUp(self):
        semester = Semester.objects.create(year=2020, term=Semester.TERM_SUMMER)
        course = Course.objects.create(
            course_code="000", department="TEST", course_title="Title", semester=semester
        )
        self.queue = Queue.objects.create(name="Queue", course=course)
        ta = User.objects.create_user("ta", "ta@a.com", "ta")
        student = User.objects.create_user("student", "student@a.com", "student")

        yesterday = timezone.localtime() - timezone.timedelta(days=1)

        self.wait_times = [100, 200, 300, 400]
        for i in range(len(self.wait_times)):
            # test all varieties of statuses
            q1 = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta,
                time_response_started=yesterday + timezone.timedelta(seconds=self.wait_times[i]),
                status=Question.STATUS_ACTIVE,
            )
            q1.time_asked = yesterday
            q1.save()

            q2 = Question.objects.create(
                text=f"Question {i + len(self.wait_times)}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta,
                time_response_started=yesterday
                + timezone.timedelta(seconds=self.wait_times[i] * 2),
                time_responded_to=yesterday + timezone.timedelta(seconds=1000),
                status=Question.STATUS_ANSWERED,
            )
            q2.time_asked = yesterday
            q2.save()

            q3 = Question.objects.create(
                text=f"Question {i + 2 * len(self.wait_times)}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta,
                time_response_started=yesterday
                + timezone.timedelta(seconds=self.wait_times[i] * 3),
                time_responded_to=yesterday,
                status=Question.STATUS_REJECTED,
            )
            q3.time_asked = yesterday
            q3.save()

        # create question that isn't in the current week
        q4 = Question.objects.create(
            text="Old question",
            queue=self.queue,
            asked_by=student,
            responded_to_by=ta,
            time_response_started=yesterday,
            status=Question.STATUS_ACTIVE,
        )
        q4.time_asked = yesterday - timezone.timedelta(weeks=2)
        q4.save()

    def test_avg_queue_wait_computation(self):
        call_command("avg_queue_wait")
        expected = sum(self.wait_times) * 6 / (len(self.wait_times) * 3)

        yesterday = timezone.datetime.today().date() - timezone.timedelta(days=1)
        last_sunday = yesterday - timezone.timedelta(days=(yesterday.weekday() + 1) % 7)
        actual = QueueStatistic.objects.get(
            queue=self.queue, metric=QueueStatistic.METRIC_AVG_WAIT, date=last_sunday
        ).value

        self.assertEqual(expected, actual)


class AverageQueueTimeHelpingTestCase(TestCase):
    def setUp(self):
        semester = Semester.objects.create(year=2020, term=Semester.TERM_SUMMER)
        course = Course.objects.create(
            course_code="000", department="TEST", course_title="Title", semester=semester
        )
        self.queue = Queue.objects.create(name="Queue", course=course)
        ta = User.objects.create_user("ta", "ta@a.com", "ta")
        student = User.objects.create_user("student", "student@a.com", "student")

        yesterday = timezone.localtime() - timezone.timedelta(days=1)

        self.help_times = [100, 200, 300, 400]
        for i in range(len(self.help_times)):
            question = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta,
                time_response_started=yesterday,
                time_responded_to=yesterday + timezone.timedelta(seconds=self.help_times[i]),
                status=Question.STATUS_ANSWERED,
            )
            question.time_asked = yesterday
            question.save()

        # create question that isn't in the current week
        old_question = Question.objects.create(
            text="Old question",
            queue=self.queue,
            asked_by=student,
            responded_to_by=ta,
            time_response_started=yesterday - timezone.timedelta(weeks=2),
            time_responded_to=yesterday - timezone.timedelta(weeks=1),
            status=Question.STATUS_ANSWERED,
        )
        old_question.time_asked = yesterday - timezone.timedelta(weeks=2)
        old_question.save()

        # create a rejected question, won't be included
        rejected = Question.objects.create(
            text="Withdrawn question",
            queue=self.queue,
            asked_by=student,
            responded_to_by=ta,
            time_response_started=yesterday,
            time_responded_to=yesterday,
            status=Question.STATUS_REJECTED,
        )
        rejected.time_asked = yesterday
        rejected.save()

    def test_avg_time_helping_computation(self):
        call_command("avg_time_helping")
        expected = sum(self.help_times) / len(self.help_times)

        yesterday = timezone.datetime.today().date() - timezone.timedelta(days=1)
        last_sunday = yesterday - timezone.timedelta(days=(yesterday.weekday() + 1) % 7)
        actual = QueueStatistic.objects.get(
            queue=self.queue, metric=QueueStatistic.METRIC_AVG_TIME_HELPING, date=last_sunday
        ).value

        self.assertEqual(expected, actual)


class AverageQueueWaitHeatmapTestCase(TestCase):
    def setUp(self):
        semester = Semester.objects.create(year=2020, term=Semester.TERM_SUMMER)
        course = Course.objects.create(
            course_code="000", department="TEST", course_title="Title", semester=semester
        )
        self.queue = Queue.objects.create(name="Queue", course=course)
        ta = User.objects.create_user("ta", "ta@a.com", "ta")
        student = User.objects.create_user("student", "student@a.com", "student")

        yesterday = timezone.localtime() - timezone.timedelta(days=1)

        self.wait_times_9 = [100, 200, 300, 400]
        for i in range(len(self.wait_times_9)):
            yesterday_9 = yesterday.replace(hour=9, minute=0)
            time_asked = (
                yesterday_9
                if i % 2 == 0
                else yesterday_9 + timezone.timedelta(weeks=-1, minutes=30)
            )
            question = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta,
                time_response_started=time_asked + timezone.timedelta(seconds=self.wait_times_9[i]),
                status=Question.STATUS_ACTIVE,
            )
            question.time_asked = time_asked
            question.save()

        self.wait_times_17 = [500, 600, 700, 800]
        for i in range(len(self.wait_times_17)):
            yesterday_17 = yesterday.replace(hour=17, minute=0)
            time_asked = (
                yesterday_17
                if i % 2 == 0
                else yesterday_17 + timezone.timedelta(weeks=-1, minutes=30)
            )
            question = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta,
                time_response_started=time_asked
                + timezone.timedelta(seconds=self.wait_times_17[i]),
                status=Question.STATUS_ACTIVE,
            )
            question.time_asked = time_asked
            question.save()

        # create question that is two days old - not included
        older = Question.objects.create(
            text="Old question",
            queue=self.queue,
            asked_by=student,
            responded_to_by=ta,
            time_response_started=yesterday_9,
            status=Question.STATUS_ACTIVE,
        )
        older.time_asked = yesterday_9 - timezone.timedelta(weeks=2, days=2)
        older.save()

    def test_avg_queue_wait_computation(self):
        call_command("avg_wait_heatmap")
        yesterday = timezone.datetime.today().date() - timezone.timedelta(days=1)
        yesterday_weekday = yesterday.weekday()

        expected_9 = sum(self.wait_times_9) / len(self.wait_times_9)
        actual_9 = QueueStatistic.objects.get(
            queue=self.queue,
            metric=QueueStatistic.METRIC_HEATMAP_WAIT,
            day=yesterday_weekday,
            hour=9,
        ).value
        self.assertEqual(expected_9, actual_9)

        expected_17 = sum(self.wait_times_17) / len(self.wait_times_17)
        actual_17 = QueueStatistic.objects.get(
            queue=self.queue,
            metric=QueueStatistic.METRIC_HEATMAP_WAIT,
            day=yesterday_weekday,
            hour=17,
        ).value
        self.assertEqual(expected_17, actual_17)

        expected_8 = 0
        actual_8 = QueueStatistic.objects.get(
            queue=self.queue,
            metric=QueueStatistic.METRIC_HEATMAP_WAIT,
            day=yesterday_weekday,
            hour=8,
        ).value
        self.assertEqual(expected_8, actual_8)


class NumberQuestionsAnsweredQueueTestCase(TestCase):
    def setUp(self):
        semester = Semester.objects.create(year=2020, term=Semester.TERM_SUMMER)
        course = Course.objects.create(
            course_code="000", department="TEST", course_title="Title", semester=semester
        )
        self.queue = Queue.objects.create(name="Queue", course=course)
        ta = User.objects.create_user("ta", "ta@a.com", "ta")
        student = User.objects.create_user("student", "student@a.com", "student")

        yesterday = timezone.localtime() - timezone.timedelta(days=1)
        self.num_questions_answered = 4

        for i in range(self.num_questions_answered):
            question = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta,
                time_response_started=yesterday - timezone.timedelta(seconds=10),
                time_responded_to=yesterday,
                status=Question.STATUS_ANSWERED,
            )
            question.time_asked = yesterday - timezone.timedelta(seconds=20)
            question.save()

        # create question that isn't in the current week
        old_question = Question.objects.create(
            text="Old question",
            queue=self.queue,
            asked_by=student,
            responded_to_by=ta,
            time_response_started=yesterday - timezone.timedelta(weeks=2),
            time_responded_to=yesterday - timezone.timedelta(weeks=1),
            status=Question.STATUS_ANSWERED,
        )
        old_question.time_asked = yesterday - timezone.timedelta(weeks=2)
        old_question.save()

        # create an active question, won't be included
        active = Question.objects.create(
            text="active question",
            queue=self.queue,
            asked_by=student,
            responded_to_by=ta,
            time_response_started=yesterday,
            time_responded_to=yesterday,
            status=Question.STATUS_ACTIVE,
        )
        active.time_asked = yesterday
        active.save()

    def test_num_questions_ans_computation(self):
        call_command("num_questions_ans")
        expected = self.num_questions_answered

        yesterday = timezone.datetime.today().date() - timezone.timedelta(days=1)
        last_sunday = yesterday - timezone.timedelta(days=(yesterday.weekday() + 1) % 7)
        actual = QueueStatistic.objects.get(
            queue=self.queue, metric=QueueStatistic.METRIC_NUM_ANSWERED, date=last_sunday
        ).value

        self.assertEqual(expected, actual)


class NumberStudentsHelpedQueueTestCase(TestCase):
    def setUp(self):
        semester = Semester.objects.create(year=2020, term=Semester.TERM_SUMMER)
        course = Course.objects.create(
            course_code="000", department="TEST", course_title="Title", semester=semester
        )
        self.queue = Queue.objects.create(name="Queue", course=course)
        ta = User.objects.create_user("ta", "ta@a.com", "ta")
        student1 = User.objects.create_user("student1", "student1@a.com", "student1")
        student2 = User.objects.create_user("student2", "student2@a.com", "student2")
        student3 = User.objects.create_user("student3", "student3@a.com", "student3")

        yesterday = timezone.localtime() - timezone.timedelta(days=1)
        students = [student1, student2, student3]
        self.number_helped = 2

        for i in range(self.number_helped):
            question = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=students[i],
                responded_to_by=ta,
                time_response_started=yesterday - timezone.timedelta(seconds=10),
                time_responded_to=yesterday,
                status=Question.STATUS_ANSWERED,
            )
            question.time_asked = yesterday - timezone.timedelta(seconds=20)
            question.save()

        # create question that isn't in the current week
        old_question = Question.objects.create(
            text="Old question",
            queue=self.queue,
            asked_by=student3,
            responded_to_by=ta,
            time_response_started=yesterday - timezone.timedelta(weeks=2),
            time_responded_to=yesterday - timezone.timedelta(weeks=1),
            status=Question.STATUS_ANSWERED,
        )
        old_question.time_asked = yesterday - timezone.timedelta(weeks=2)
        old_question.save()

        # create an active question, won't be included
        active = Question.objects.create(
            text="active question",
            queue=self.queue,
            asked_by=student3,
            responded_to_by=ta,
            time_response_started=yesterday,
            time_responded_to=yesterday,
            status=Question.STATUS_ACTIVE,
        )
        active.time_asked = yesterday
        active.save()

    def test_num_students_helped_computation(self):
        call_command("num_students_helped")
        expected = self.number_helped

        yesterday = timezone.datetime.today().date() - timezone.timedelta(days=1)
        last_sunday = yesterday - timezone.timedelta(days=(yesterday.weekday() + 1) % 7)
        actual = QueueStatistic.objects.get(
            queue=self.queue, metric=QueueStatistic.METRIC_STUDENTS_HELPED, date=last_sunday
        ).value

        self.assertEqual(expected, actual)


class QuestionsPerTAQueueHeatmapTestCase(TestCase):
    def setUp(self):
        semester = Semester.objects.create(year=2020, term=Semester.TERM_SUMMER)
        course = Course.objects.create(
            course_code="000", department="TEST", course_title="Title", semester=semester
        )
        self.queue = Queue.objects.create(name="Queue", course=course)
        ta1 = User.objects.create_user("ta1", "ta1@a.com", "ta1")
        ta2 = User.objects.create_user("ta2", "ta2@a.com", "ta2")
        student = User.objects.create_user("student", "student@a.com", "student")

        self.num_tas_8 = 1
        self.num_tas_17 = 2

        yesterday = timezone.localtime() - timezone.timedelta(days=1)

        self.ta_1_questions_8 = 3
        for i in range(self.ta_1_questions_8):
            yesterday_8 = yesterday.replace(hour=8, minute=0)
            time_asked = (
                yesterday_8
                if i % 2 == 0
                else yesterday_8 + timezone.timedelta(weeks=-1, minutes=30)
            )
            question = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta1,
                time_response_started=time_asked + timezone.timedelta(minutes=10),
                status=Question.STATUS_ACTIVE if i % 3 == 0 else Question.STATUS_ANSWERED,
            )
            question.time_asked = time_asked
            question.save()

        self.ta_1_questions_17 = 3
        self.ta_2_questions_17 = 4
        for i in range(self.ta_1_questions_17 + self.ta_2_questions_17):
            yesterday_17 = yesterday.replace(hour=17, minute=0)
            time_asked = (
                yesterday_17
                if i % 2 == 0
                else yesterday_17 + timezone.timedelta(weeks=-1, minutes=59)
            )
            question = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta1 if i < self.ta_1_questions_17 else ta2,
                time_response_started=time_asked + timezone.timedelta(minutes=10),
                status=Question.STATUS_ACTIVE if i % 3 == 0 else Question.STATUS_ANSWERED,
            )
            question.time_asked = time_asked
            question.save()

        # create question that is two days old - not included
        older = Question.objects.create(
            text="Old question",
            queue=self.queue,
            asked_by=student,
            responded_to_by=ta2,
            time_response_started=yesterday_8,
            status=Question.STATUS_ACTIVE,
        )
        older.time_asked = yesterday_8 - timezone.timedelta(weeks=2, days=2)
        older.save()

    def test_questions_per_ta_computation(self):
        call_command("questions_per_ta_heatmap")
        yesterday = timezone.datetime.today().date() - timezone.timedelta(days=1)
        yesterday_weekday = yesterday.weekday()

        expected_8 = self.ta_1_questions_8 / self.num_tas_8
        actual_8 = QueueStatistic.objects.get(
            queue=self.queue,
            metric=QueueStatistic.METRIC_HEATMAP_QUESTIONS_PER_TA,
            day=yesterday_weekday,
            hour=8,
        ).value
        self.assertEqual(expected_8, actual_8)

        expected_17 = (self.ta_1_questions_17 + self.ta_2_questions_17) / self.num_tas_17
        actual_17 = QueueStatistic.objects.get(
            queue=self.queue,
            metric=QueueStatistic.METRIC_HEATMAP_QUESTIONS_PER_TA,
            day=yesterday_weekday,
            hour=17,
        ).value
        self.assertEqual(expected_17, actual_17)


class AverageQueueWaitTimeByDateTestCase(TestCase):
    def setUp(self):
        semester = Semester.objects.create(year=2020, term=Semester.TERM_SUMMER)
        course = Course.objects.create(
            course_code="000", department="TEST", course_title="Title", semester=semester
        )
        self.queue = Queue.objects.create(name="Queue", course=course)
        ta = User.objects.create_user("ta", "ta@a.com", "ta")
        student = User.objects.create_user("student", "student@a.com", "student")

        yesterday = timezone.localtime() - timezone.timedelta(days=1)

        # this command computes avg wait time yesterday
        self.wait_times = [100, 200, 300, 400]
        for i in range(len(self.wait_times)):
            # test all varieties of statuses
            q1 = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta,
                time_response_started=yesterday + timezone.timedelta(seconds=self.wait_times[i]),
                status=Question.STATUS_ACTIVE,
            )
            q1.time_asked = yesterday
            q1.save()

            q2 = Question.objects.create(
                text=f"Question {i + len(self.wait_times)}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta,
                time_response_started=yesterday
                + timezone.timedelta(seconds=self.wait_times[i] * 2),
                time_responded_to=yesterday + timezone.timedelta(seconds=1000),
                status=Question.STATUS_ANSWERED,
            )
            q2.time_asked = yesterday
            q2.save()

            q3 = Question.objects.create(
                text=f"Question {i + 2 * len(self.wait_times)}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta,
                time_response_started=yesterday
                + timezone.timedelta(seconds=self.wait_times[i] * 3),
                time_responded_to=yesterday + timezone.timedelta(seconds=self.wait_times[i] * 3),
                status=Question.STATUS_REJECTED,
            )
            q3.time_asked = yesterday
            q3.save()

        # create question that wasn't yesterday
        q4 = Question.objects.create(
            text="Old question",
            queue=self.queue,
            asked_by=student,
            responded_to_by=ta,
            time_response_started=yesterday - timezone.timedelta(days=1),
            status=Question.STATUS_ACTIVE,
        )
        q4.time_asked = yesterday - timezone.timedelta(days=2)
        q4.save()

    def test_wait_time_days_computation(self):
        call_command("wait_time_days")
        expected = sum(self.wait_times) * 6 / (len(self.wait_times) * 3)

        yesterday = timezone.datetime.today().date() - timezone.timedelta(days=1)
        actual = QueueStatistic.objects.get(
            queue=self.queue, metric=QueueStatistic.METRIC_LIST_WAIT_TIME_DAYS, date=yesterday
        ).value

        self.assertEqual(expected, actual)


class QuestionsPerTAQueueHeatmapHistTestCase(TestCase):
    def setUp(self):
        semester = Semester.objects.create(year=2020, term=Semester.TERM_SUMMER)
        course = Course.objects.create(
            course_code="000", department="TEST", course_title="Title", semester=semester
        )
        self.queue = Queue.objects.create(name="Queue", course=course)
        ta1 = User.objects.create_user("ta1", "ta1@a.com", "ta1")
        ta2 = User.objects.create_user("ta2", "ta2@a.com", "ta2")
        student = User.objects.create_user("student", "student@a.com", "student")

        self.num_tas_8 = 1
        self.num_tas_17 = 2

        yesterday = timezone.localtime() - timezone.timedelta(days=1)

        self.ta_1_questions_8 = 3
        for i in range(self.ta_1_questions_8):
            yesterday_8 = yesterday.replace(hour=8, minute=0)
            time_asked = (
                yesterday_8
                if i % 2 == 0
                else yesterday_8 + timezone.timedelta(weeks=-1, minutes=30)
            )
            question = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta1,
                time_response_started=time_asked + timezone.timedelta(minutes=10),
                status=Question.STATUS_ACTIVE if i % 3 == 0 else Question.STATUS_ANSWERED,
            )
            question.time_asked = time_asked
            question.save()

        self.ta_1_questions_17 = 3
        self.ta_2_questions_17 = 4
        for i in range(self.ta_1_questions_17 + self.ta_2_questions_17):
            yesterday_17 = yesterday.replace(hour=17, minute=0)
            time_asked = (
                yesterday_17
                if i % 2 == 0
                else yesterday_17 + timezone.timedelta(weeks=-1, minutes=59)
            )
            question = Question.objects.create(
                text=f"Question {i}",
                queue=self.queue,
                asked_by=student,
                responded_to_by=ta1 if i < self.ta_1_questions_17 else ta2,
                time_response_started=time_asked + timezone.timedelta(minutes=10),
                status=Question.STATUS_ACTIVE if i % 3 == 0 else Question.STATUS_ANSWERED,
            )
            question.time_asked = time_asked
            question.save()

        # create question that is two days old - not included
        self.older_time_asked = yesterday_8 - timezone.timedelta(weeks=2, days=2)
        self.older_time_asked.replace(hour=8, minute=0)
        older = Question.objects.create(
            text="Old question",
            queue=self.queue,
            asked_by=student,
            responded_to_by=ta2,
            time_response_started=self.older_time_asked + timezone.timedelta(minutes=5),
            status=Question.STATUS_ACTIVE,
        )
        older.time_asked = self.older_time_asked
        older.save()

    def test_questions_per_ta_computation(self):
        call_command("questions_per_ta_heatmap_hist")
        yesterday = timezone.datetime.today().date() - timezone.timedelta(days=1)
        yesterday_weekday = yesterday.weekday()

        expected_8 = self.ta_1_questions_8 / self.num_tas_8
        actual_8 = QueueStatistic.objects.get(
            queue=self.queue,
            metric=QueueStatistic.METRIC_HEATMAP_QUESTIONS_PER_TA,
            day=yesterday_weekday,
            hour=8,
        ).value
        self.assertEqual(expected_8, actual_8)

        expected_17 = (self.ta_1_questions_17 + self.ta_2_questions_17) / self.num_tas_17
        actual_17 = QueueStatistic.objects.get(
            queue=self.queue,
            metric=QueueStatistic.METRIC_HEATMAP_QUESTIONS_PER_TA,
            day=yesterday_weekday,
            hour=17,
        ).value
        self.assertEqual(expected_17, actual_17)

        expected_two_days_ago_8 = 1
        actual_two_days_ago_8 = QueueStatistic.objects.get(
            queue=self.queue,
            metric=QueueStatistic.METRIC_HEATMAP_QUESTIONS_PER_TA,
            day=self.older_time_asked.weekday(),
            hour=8,
        ).value
        self.assertEqual(expected_two_days_ago_8, actual_two_days_ago_8)
