from docker_tools import DockerHubManager

manager = DockerHubManager()


def get_repos():
    repos = manager.get_repos()
    return repos


def get_tags_by_repo(repo):
    tags = manager.get_tags_by_repo(repo)
    return tags


fname2fctn = {'get_tags_by_repo': get_tags_by_repo,
              'get_repos': get_repos}


def lambda_handler(event, context):
    fname = event['fctn']
    args = tuple(event.get('args', []))
    kwargs = event.get('kwargs', {})

    if fname in fname2fctn:
        result = fname2fctn[fname](*args, **kwargs)

        return {
            'statusCode': 200,
            'result': result
        }
    else:
        return {
            'statusCode': 404,
            'msg': 'Function not found!'
        }
