
import json
import time
import requests


def get_questions(url, params):
    """
    GET questions from stackoverflow at the given
    url with the given parameters.  Will write it out
    to a file for local caching.

    Expect 'tagged' and 'page' to be among parameters
    and has_more in the response.
    """
    try:
        response = requests.get(url, params=params)
        if response.status_code == requests.codes.ok:
            filename = params['tagged'] + '_' + str(params['page']) + '.json'
            print(filename)
            with open(filename, 'w') as output:
                body = response.json()
                json.dump(body, output, indent=4)
                return body['has_more']

    except Exception,e:
        print(response.status_code)
        print(e)
        response.raise_for_status()

    return False

def get_all_questions(tag, page=1):
    """
    GET all questions for the given tag one page
    at a time.
    """
    limit = 50

    url = 'https://api.stackexchange.com/2.2/questions'
    params = {
        'page': page,
        'pagesize': 100,
        'order': 'asc',
        'sort': 'creation',
        'tagged': tag,
        'site': 'stackoverflow',
        }
    print("Fetching Questions on {}".format(tag))
    while get_questions(url, params):
        params['page'] = params['page'] + 1

        limit -= 1
        if limit < 0:
            break

def get_cache(tag, page, output):
    filename = tag + '_' + str(page) + '.json'
    print(filename)
    try:
        with open(filename, 'r') as data:
            questions = json.load(data)

            for item in questions['items']:
                created = time.strftime('%Y-%m-%d',
                        time.localtime(float(item['creation_date'])))
                active = time.strftime('%Y-%m-%d',
                        time.localtime(float(item['last_activity_date'])))

                output.write(','.join(map(str, [
                        'TODO',
                        created,
                        active,
                        item['question_id'],
                        item['is_answered'],
                        item['answer_count'],
                        item['view_count'],
                        item['score'],
                        item['link'],
                    ])) + '\n')
        return True

    except Exception,e:
        # gross hack
        print(e)
        return False

def combine(tag):
    """
    Read local cache of questions and combine into a
    tracking file.
    """
    page = 1
    filename = tag + '.csv'
    with open(filename, 'w') as output:
        output.write(','.join([
            'status',
            'creation_date',
            'last_activity_date',
            'question_id',
            'is_answered',
            'answer_count',
            'view_count',
            'score',
            'link'
            ]) + "\n")
        while get_cache(tag, page, output):
            page += 1


# not proud of this, but works for now
tag = 'geojson'
# get_all_questions(tag, page=25)
combine(tag)

