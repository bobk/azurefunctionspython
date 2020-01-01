
# http://github.com/bobk/azurefunctionspython
#
# sample Python code that demonstrates:
#    - simple Azure Function written in Python
#    - basic use of jira-python library https://github.com/pycontribs/jira
#    - calculation of a single Jira metric (number of In Progress issues for a given username)

import logging
import azure.functions as func

from jira import JIRA

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Starting processing')

    server = req.params.get('server')
    project = req.params.get('project')
    assignee = req.params.get('assignee')
    username = req.params.get('username')
    userpassword = req.params.get('userpassword')

    if ((not server) or (not project) or (not assignee) or (not username) or (not userpassword)):
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            server = req_body.get('server')
            project = req_body.get('project')
            assignee = req.params.get('assignee')
            username = req_body.get('username')
            userpassword = req_body.get('userpassword')

    logging.info("parameters:")
    logging.info("server: {server}\r   project: {project}   assignee: {assignee}   username: {username}   userpassword: ***")

    if ((server) and (project) and (assignee) and (username) and (userpassword)):

        retstring = ""
        retstring += f"server: {server}\r   project: {project}   assignee: {assignee}   username: {username}   userpassword: ***"

        try:
            logging.info("starting Jira connection")
            jiraoptions = { "server": "http://" + server }
            jiraconn = JIRA(jiraoptions, basic_auth=(username, userpassword))
        except:
            logging.info("exception occurred")
            retstring += "exception occurred"
        else:
            issues = jiraconn.search_issues(f"project in ({project}) and assignee in ({assignee}) and statusCategory in (\"In Progress\") order by createdDate desc", startAt=0, maxResults=0)
            numissues = len(issues)
            retstring += ("num issues = " + str(numissues))
            jiraconn.close()

        return func.HttpResponse(retstring, status_code=200)
    
    
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )


