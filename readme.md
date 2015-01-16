# ionitron-issues
[ionitron-issues.herokuapp.com](http://ionitron-issues.herokuapp.com/)

*Teaching Ionitron to handle Github issues.*

### Overview:


ionitron-github is a github bot that watches the Ionic repo, and will take action when certain **webhook** events are received. Ionitron also performs a number of repo maintenance tasks that are triggered by daily **cronjobs**. All actions can be customized by changing the variables in `config.py`. See [config.py](https://github.com/driftyco/ionitron-issues/blob/master/config.py) for a full list of options. Below is a checklist outlining current and future features.

### Running Locally / Development:

***1:)*** install the Python (2.7.3) dependencies:
```
pip install -r requirements.txt
```
***2:)*** Add the following environmental variables to `.bashrc` or virtualenv script:
```
export GITHUB_USERNAME='ionitron'
export GITHUB_PASSWORD='supersecretpassword'
export REPO_USERNAME='driftyco'
export REPO_ID='ionic'
export WARNING_TEMPLATE='https://raw.githubusercontent.com/driftyco/ionitron-lingo/master/templates/cron/warning.md'
export CLOSING_TEMPLATE='https://raw.githubusercontent.com/driftyco/ionitron-lingo/master/templates/cron/closed.md'
export CLOSING_NOREPLY_TEMPLATE='https://raw.githubusercontent.com/driftyco/ionitron-lingo/master/templates/cron/closed_noreply.md'
export RESUBMIT_TEMPLATE='https://raw.githubusercontent.com/driftyco/ionitron-lingo/master/templates/webhooks/resubmit.md'
```
*The template variables can be changed to point to a local file to test messages on a test repo. This is useful to test repo webhooks, and the responses that should be returned.*

***3:)*** Install [redis-server](http://redis.io/topics/quickstart). This is used as a task queue for cron jobs such as removing old issues, updating issue scores, etc. It is also used as a cache; issue data is persisted and updated daily, or when the issue receives an update event. Finally, redis stores common data about the repo, organization, contributors, etc. Redis-server needs to be started in the background before the app can be run:
```
$ redis-server
```
***4:)*** start the app server by running `python main.py`


### Debug Mode:
If `debug=True`, all of the cronjob tasks below will *run*, but won't take action to close/warn the issues. Instead, the issues that would have been closed/warned are printed out to the console. This is useful if you want to tweak the configurations, and see how the changes impact what should be closed/warned, without actually doing it.

### Deploying:
```
$ heroku git:remote -a ionitron-issues
$ git push heroku master
```
Check out [this article](https://devcenter.heroku.com/articles/git) for more info. The redis-to-go addon must be configured if starting from a new Heroku app.




### Cronjob Tasks:

- [x] **/api/warn-old-issues** - warns github issues older than $WARN_INACTIVE_AFTER days that it will soon be removed. Adds a comment based on the local or remote markdown template defined in $WARNING_TEMPLATE.
- [x] **/api/close-old-issues** - closes github issues older than $CLOSE_INACTIVE_AFTER days. Adds a comment based on the local or remote markdown template defined in $CLOSING_TEMPLATE.
- [x] **/api/close-noreply-issues** - closes github issues that haven't received a reply after $CLOSE_NOREPLY_AFTER days after the `needs reply` label has been added. Adds a comment based on the local or remote markdown template defined in $CLOSING_NOREPLY_TEMPLATE.
- [x] - run all tasks daily. If necessary, [the interface](http://ionitron-issues.herokuapp.com/) can be used to manually trigger the tasks above.

### Webhooks Tasks:

- [x] checks all commit titles in pull requests against Angular's [commit convention guidelines](https://github.com/angular/angular.js/blob/master/CONTRIBUTING.md#commit). Status will be set to either *success* or *failure*.
- [x] adds a comment to all issues not submitted through Ionic's [issue submit form](http://ionicframework.com/submit-issue/) containing a link to resubmit the issue. Also adds the *ionitron: please resubmit* label to the issue.
- [x] removes the comment prompting the user to resubmit the issue when they resubmit it using the form. Also removes the *ionitron: please resubmit* label.

### Ideas/Todo:

- [ ] remove issues not resubmitted within 7 days
- [ ] configure ionic-site endpoint, run deployment script whenever documentation is updated
- [ ] add scoring algorithm to determine whether it's likely a codepen or additional will be required. If so, prompt for a codepen in the Ionic issue form.
- [x] add a general issue scoring algorithm based on issue/user metadata. Add a simple interface to view the results.
- [ ] if an issue submitted through github resembles a feature request, instead of pushing the issue through the custom form, add link to Ionic's [feature request board](https://trello.com/b/nNk2Yq1k/ionic-framework)
