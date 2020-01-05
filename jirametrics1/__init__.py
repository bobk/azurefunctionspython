
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
from http import HTTPStatus
from jira import JIRA

#   Input bindings are passed in via parameters to main()
def main(req: func.HttpRequest) -> func.HttpResponse:
#   Write to the Azure Functions log stream.
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
        assignee = req_body.get('assignee')
        username = req_body.get('username')
        userpassword = req_body.get('userpassword')

#   perform the query
    if ((server) and (project) and (assignee) and (username) and (userpassword)):
        logging.info(f"variables:   server =  {server}   project = {project}   assignee = {assignee}   username = {username}   userpassword = ***")

        try:
            logging.info("opening Jira connection")
            jiraoptions = {"server": "http://" + server, "max_retries": 0}
#   username = Atlassian Cloud Jira Server user ID email address, userpassword = an API token generated under that user ID
            try:
                jiraconn = JIRA(jiraoptions, basic_auth=(username, userpassword))
#   were we able to connect?
                logging.info("successful connection")
                logging.info("running query")
                issues = jiraconn.search_issues(f"project in ({project}) and assignee in ({assignee}) and statusCategory in (\"In Progress\")", startAt=0, maxResults=0)
                status = HTTPStatus.OK
                statusstr = "successful query: number of In Progress issues for {assignee} = " + str(len(issues))
#   always attempt to close the connection regardless
                logging.info(statusstr)
                logging.info("closing Jira connection")
                jiraconn.close()
            except JIRAError:
#   if not, adjust the HTTP status code and string appropriately
                status = HTTPStatus.FORBIDDEN
                statusstr = "unsuccessful connection (username/userpassword variables invalid?): no data"
#   in case something unexpected happens
        except:
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            statusstr = "exception occurred during connection or query: no data"

    else:
        status = HTTPStatus.BAD_REQUEST
        statusstr = "error retrieving variables: please pass the variables as either GET or POST"

    logging.info("ending processing")
    #   create HTTP response
    return func.HttpResponse(status_code=status, body=statusstr)
