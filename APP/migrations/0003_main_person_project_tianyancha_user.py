# Generated by Django 4.1.7 on 2023-03-14 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APP', '0002_alter_user_name_alter_user_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='Main_person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pname', models.CharField(max_length=80, verbose_name='姓名')),
                ('position', models.CharField(max_length=80, verbose_name='职位')),
            ],
            options={
                'verbose_name': '主要人员',
                'verbose_name_plural': '主要人员',
                'db_table': 'main_person',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=80, verbose_name='项目编号')),
                ('project_name', models.CharField(max_length=80, verbose_name='项目名称')),
                ('project_place', models.CharField(max_length=80, verbose_name='项目属地')),
                ('project_type', models.CharField(max_length=80, verbose_name='项目类型')),
                ('construct_company', models.CharField(max_length=80, verbose_name='建设单位')),
            ],
            options={
                'verbose_name': '项目',
                'verbose_name_plural': '项目',
                'db_table': 'project',
            },
        ),
        migrations.CreateModel(
            name='Tianyancha_User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=80, unique=True, verbose_name='手机号')),
                ('password', models.CharField(max_length=80, verbose_name='密码')),
            ],
            options={
                'verbose_name': '天眼查用户',
                'verbose_name_plural': '天眼查用户',
                'db_table': 'tianyancha_user',
            },
        ),
    ]
