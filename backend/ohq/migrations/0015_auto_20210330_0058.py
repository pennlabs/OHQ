# Generated by Django 3.1.7 on 2021-03-30 00:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ohq', '0014_delete_membershipstatistic'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipStatistic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric', models.CharField(choices=[('STUDENT_AVG_TIME_HELPED', 'Student: Average time being helped'), ('STUDENT_AVG_TIME_WAITING', 'Student: Average time waiting for help'), ('INSTR_AVG_TIME_HELPING', 'Instructor: Average time helping per question'), ('INSTR_AVG_STUDENTS_PER_HOUR', 'Instructor: Average number of students helped per hour')], max_length=256)),
                ('value', models.DecimalField(decimal_places=8, max_digits=16)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ohq.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='membershipstatistic',
            constraint=models.UniqueConstraint(fields=('user', 'course', 'metric'), name='membership_statistic'),
        ),
    ]
