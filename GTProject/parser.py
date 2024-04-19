import pdb
import csv
import os
# Python이 실행될 때 DJANGO_SETTINGS_MODULE이라는 환경 변수에 현재 프로젝트의 settings.py파일 경로를 등록한다.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GTProject.settings")
import django
django.setup()
from TopicsTrending.models import *
from django.db.utils import IntegrityError
from datetime import datetime

current_dir = os.getcwd()
data_path = os.path.join(current_dir, 'assets', 'data')
img_path = os.path.join(current_dir, 'assets', 'img')


def job_data_parser():
    # CSV 파일 경로
    file_path = os.path.join(data_path, 'job_data.csv')

    # CSV 파일 열기
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        # CSV 파일을 읽어들이는데 사용할 reader 생성
        reader = csv.reader(csvfile)
        # reader 객체를 subscriptable하게 만들기 위해 각 행을 리스트로 저장
        rows = [row for row in reader]
        result, all_stack = job_skill_refactor(rows)

    return result, all_stack


def job_skill_refactor(rows):
    # 각 행을 순회하면서 데이터 읽기
    result = {}
    all_stack = set()

    for row in rows[1:]:
        categories = row[1].split(', ')
        skills = eval(row[2])
        # for category, skill_list in zip(categories, skills):
        #     category_dict = result.get(category, {})
        #     for skill in skills:
        #         category_dict[skill] = category_dict.get(skill, 0) + 1
        #
        #     result[category] = category_dict
        #
        # for category in result:
        #     result[category] = dict(sorted(result[category].items(), key=lambda x: x[1], reverse=True))
        for category in categories:
            if category not in result:
                result[category] = []
            for skill in skills:
                result[category].append(skill)

    for category in result:
        all_stack = all_stack | set(result[category])

    # len(result) 25 erp 빠짐
    # list(my_dict.keys())
    return result, all_stack


def job_skill_DB_loader(job_skill):
    for key in job_skill:
        print(job_skill[key])
        job = Job.objects.create(name=key)
        for skill in job_skill[key]:
            Skill.objects.create(name=skill, job=job, name_job_id=key)


def git_repo_parser(skills):

    # CSV 파일 경로
    file_path = os.path.join(data_path, 'git')
    git_img_path = os.path.join(img_path, 'git')
    for skill in os.listdir(file_path):
        # git CSV 파일 먼저 파싱
        skill_path = os.path.join(file_path, skill)
        for csv_file in os.listdir(skill_path):
            csv_path = os.path.join(skill_path, csv_file)
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                # CSV 파일을 읽어들이는데 사용할 reader 생성
                reader = csv.reader(csvfile)
                # reader 객체를 subscriptable하게 만들기 위해 각 행을 리스트로 저장
                rows = [row for row in reader]

            # git 이미지 파일 파싱
            skill_path = os.path.join(git_img_path, skill)
            for img_file in os.listdir(skill_path):
                if csv_path[-9:] == 'forks.csv':
                    git_img_file_path = os.path.join(skill_path, 'forks')
                    for i, img in enumerate(os.listdir(git_img_file_path)):
                        rows[i+1].append(os.path.join(git_img_file_path, img))
                elif csv_path[-9:] == 'stars.csv':
                    git_img_file_path = os.path.join(skill_path, 'stars')
                    for i, img in enumerate(os.listdir(git_img_file_path)):
                        rows[i + 1].append(os.path.join(git_img_file_path, img))

            git_repo_DB_loader(skill, rows[1:])
    # return result, all_stack


def git_repo_DB_loader(skill, repo_infos):
    for info in repo_infos:
        print(info)
        tech_stack = Skill.objects.filter(name=skill).first()
        formatted_date_string = info[4].replace(',', '')
        formatted_date_string = formatted_date_string.replace('GMT+9', '+0900')
        date_time_obj = datetime.strptime(formatted_date_string, '%b %d %Y %I:%M %p %z')

        try:
            Repository.objects.create(skill=tech_stack,
                                      repo_title=info[0],
                                      repo_forks=int(info[1].replace(',', '')),
                                      repo_stars=int(info[2].replace(',', '')),
                                      repo_recent_time=date_time_obj,
                                      repo_writer=info[5],
                                      repo_url=info[6],
                                      repo_img=info[7] if len(info) == 8 else "")
        except IntegrityError:
            pass

if __name__ == '__main__':

    job_skill, all_skill = job_data_parser()
    job_skill_DB_loader(job_skill)

    git_repo_parser(sorted(list(all_skill)))




