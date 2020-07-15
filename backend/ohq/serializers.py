from django.conf import settings
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from ohq.models import Course, Membership, MembershipInvite, Profile, Question, Queue, Semester


class CourseRouteMixin(serializers.ModelSerializer):
    """
    Mixin for serializers that overrides the save method to
    properly handle the URL parameter for courses.
    """

    def save(self):
        self.validated_data["course"] = Course.objects.get(
            pk=self.context["view"].kwargs["course_pk"]
        )
        return super().save()


class QueueRouteMixin(serializers.ModelSerializer):
    """
    Mixin for serializers that overrides the save method to
    properly handle the URL parameter for queues.
    """

    def save(self):
        self.validated_data["queue"] = Queue.objects.get(pk=self.context["view"].kwargs["queue_pk"])
        return super().save()


class ProfileSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField()

    class Meta:
        model = Profile
        fields = ("preferred_name", "sms_notifications_enabled", "phone_number")


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=False)

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ("last_name", "email", "profile")

    # TODO: need to add logic to update profile from here


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ("year", "term")


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "course_code",
            "department",
            "course_title",
            "description",
            "semester",
            "archived",
            "invite_only",
            "video_chat_enabled",
            "require_video_chat_url_on_questions",
            # "members",
        )


class QueueSerializer(CourseRouteMixin):
    class Meta:
        model = Queue
        fields = (
            "id",
            "name",
            "description",
            "archived",
            "estimated_wait_time",
            "start_end_times",
            "active_override_time",
        )


# TODO: show different serializers if your a prof/TA or student
class QuestionSerializer(QueueRouteMixin):
    class Meta:
        model = Question
        fields = (
            "text",
            "video_chat_url",
            "time_asked",
            "asked_by",
            "time_last_updated",
            "time_withdrawn",
            "time_rejected",
            "rejected_by",
            "rejected_reason",
            "rejected_reason_other",
            "time_started",
            "time_answered",
            "answered_by",
            "should_send_up_soon_notification",
        )


# TODO: membership serializers