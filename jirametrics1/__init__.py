
# http://github.com/bobk/azurefunctionspython
#
# sample Python code that demonstrates:
#    - simple Azure Function written in Python
#    - basic use of jira-python library https://github.com/pycontribs/jira
#    - calculation of a single Jira metric (number of In Progress issues for which a given username is Assignee)
#
# this is a demo of Azure Functions and the jira-python library and is not intended to be an exhaustive sample of error checking every Jira operation
#   

import logging
import azure.functions as func

from jira import JIRA

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("starting processing")

#   we need these 5 variables to calculate metrics - note that no user credentials are stored or cached anywhere
    logging.info("looking in GET parameters for variables")
    server = req.params.get('server')
    project = req.params.get('project')
    assignee = req.params.get('assignee')
    username = req.params.get('username')
    userpassword = req.params.get('userpassword')

#   ensure that all the variables are populated via the GET, if not check the POST
    if ((not server) or (not project) or (not assignee) or (not username) or (not userpassword)):
        logging.info("not all variables found via GET, looking in POST")
        req_body = req.get_json()
        server = req_body.get('server')
        project = req_body.get('project')
        assignee = req.params.get('assignee')
        username = req_body.get('username')
        userpassword = req_body.get('userpassword')

#   perform the query
    if ((server) and (project) and (assignee) and (username) and (userpassword)):
        logging.info(f"variables:   server =  {server}   project = {project}   assignee = {assignee}   username = {username}   userpassword = ***")

        try:
            logging.info("opening Jira connection")
            jiraoptions = {"server": "http://" + server}
#   username = Atlassian Cloud Jira Server user ID email address, userpassword = an API token generated under that user ID
            jiraconn = JIRA(jiraoptions, basic_auth=(username, userpassword))
            logging.info("running Jira query")
            issues = jiraconn.search_issues(f"project in ({project}) and assignee in ({assignee}) and statusCategory in (\"In Progress\") order by createdDate desc", startAt=0, maxResults=0)
        except:
            statusstr = "exception occurred during connection or query: no data"
        else:
            statusstr = "successful connection and query: num open issues = " + str(len(issues))

        logging.info(statusstr)
        logging.info("closing Jira connection")
        jiraconn.close()
        return func.HttpResponse(statusstr, status_code=200)
    else:
        return func.HttpResponse("error retrieving variables: please pass the variables as either GET or POST", status_code=400)
