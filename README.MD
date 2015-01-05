# ionitron-issues
[ionitron-issues.herokuapp.com](http://ionitron-issues.herokuapp.com/)

*Teaching Ionitron to handle Github issues.*

### Overview:


ionitron-github is a github bot that watches the Ionic repo, and will take action when certain **webhook** events are received. Ionitron also performs a number of repo maintenance tasks that are triggered by daily **cronjobs**. All actions can be customized by changing the variables in `config.py`. See [config.py](https://github.com/driftyco/ionitron-issues/blob/master/config.py) for a full list of options. Below is a checklist outlining current and future features.

### Cronjob Tasks

- [x] **/api/warn-old-issues** - warns github issues older than $WARN_INACTIVE_AFTER days that it will soon be removed. Adds a comment based on the local or remote markdown template defined in $WARNING_TEMPLATE.
- [x] **/api/close-old-issues** - closes github issues older than $CLOSE_INACTIVE_AFTER days. Adds a comment based on the local or remote markdown template defined in $CLOSING_TEMPLATE.
- [x] **/api/close-noreply-issues** - closes github issues that haven't received a reply after $CLOSE_NOREPLY_AFTER days after the `needs reply` label has been added. Adds a comment based on the local or remote markdown template defined in $CLOSING_NOREPLY_TEMPLATE.
- [x] - run all tasks daily. If necessary, [the interface](http://ionitron-issues.herokuapp.com/) can be used to manually trigger the tasks above.

### Webhooks Tasks:

- [x] - checks all commit titles in pull requests against Angular's [commit convention guidelines](https://github.com/angular/angular.js/blob/master/CONTRIBUTING.md#commit). Status will be set to either *success* or *failure*.
- [x] - adds a comment to all issues not submitted through Ionic's [issue submit form](http://ionicframework.com/submit-issue/) containing a link to resubmit the issue. Also adds the *ionitron: please resubmit* label to the issue.
- [x] - removes the comment prompting the user to resubmit the issue when they resubmit it using the form. Also removes the *ionitron: please resubmit* label.

### Ideas/Todo:

- [ ] - remove issues not resubmitted within 7 days
- [ ] - configure ionic-site endpoint, run deployment script whenever documentation is updated
- [ ] - add scoring algorithm to determine whether it's likely a codepen or additional will be required. If so, prompt for a codepen in the Ionic issue form.
- [ ] - add a general issue scoring algorithm based on issue/user metadata. Add a simple interface to view the results.
- [ ] - if an issue submitted through github resembles a feature request, instead of pushing the issue through the custom form, add link to Ionic's [feature request board](https://trello.com/b/nNk2Yq1k/ionic-framework)
