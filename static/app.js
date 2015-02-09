angular.module('app', ['ui.router', 'ngGrid'])

.config(function($stateProvider, $urlRouterProvider) {

  $stateProvider

    .state('manage', {
      url: "/manage",
      templateUrl: "/partials/manage.html",
      controller: 'AppCtrl',
    })

    .state('issues', {
      url: "/",
      templateUrl: "/partials/issues.html",
      controller: 'IssueListCtrl',
    });

  $urlRouterProvider.otherwise('/');

})


.controller('AppCtrl', function($scope, $http){

    $scope.response = {'text': 'Nothing to show. Click below to manually trigger a cron task.'};

    $scope.manualCron = function(location){
      $scope.response.text = 'Making request. This might take a while...';
      $http.get('/api/' + location)
        .success(function(data){
          $scope.response.text = JSON.stringify(data);
        })
        .error(function(data){
          $scope.response.text = JSON.stringify(data);
        });
    };
})

.controller('IssueListCtrl', function($scope, $location, ScoreFactory){

    $scope.isLoading = true;
    $scope.issue_data = [];

    $scope.gridOptions = {
        data: 'issue_data',
        sortInfo: { fields: ['score'], directions: ['desc']},
        columnDefs: [
          {field: 'index', displayName:'', width: '3%', cellFilter: 'number:0'},
          {field: 'number', displayName:'Issue #', width:'5%',
                      cellTemplate: '<div class="ngCellText"><a href="{{repo_data.repo_url}}/issues/{{row.getProperty(col.field)}}" target="_blank">#<span ng-cell-text>{{row.getProperty(col.field)}}</span></a></div>'},
          {field: 'score', displayName:'Score', width: '6%', cellFilter: 'number:0',
                      cellTemplate: '<div class="ngCellText"  title="{{row.getProperty(\'score_data\') | scoreData}}"><span ng-cell-text>{{row.getProperty(col.field)}}</span></div>'},
          {field: 'comments', displayName:'Comments', width: '5%', cellFilter: 'number:0'},
          {field: 'references', displayName:'Refs', width: '3%', cellFilter: 'number:0'},
          {field: 'created', displayName: 'Created', width: '7%', cellFilter: 'date:"MM/dd/yy"'},
          {field: 'updated', displayName: 'Updated', width: '7%', cellFilter: 'date:"MM/dd/yy"'},
          {field: 'username', displayName:'User', width: '10%', cellTemplate: '<div class="ngCellText"><img class="thumb" ng-src="{{row.getProperty(\'avatar\')}}"><a href="http://github.com/{{row.getProperty(col.field)}}" target="_blank"><span ng-cell-text>{{row.getProperty(col.field)}}</span></a></div>'},
          {field: 'title', displayName: 'Title', width: '38%'},
          {field: 'assignee', displayName: 'Assignee', width: '8%'},
          {field: 'milestone', displayName: 'MS', width: '8%'},
        ],
        multiSelect: false,
        afterSelectionChange: afterSelectionChange
    };

    function afterSelectionChange(rowItem, event) {
      if (!rowItem.selected) return;
      $scope.issueDetail = angular.copy(rowItem.entity);
      $scope.issueDetail.actionType = 'close';
      $scope.issueDetail.messageType = '';
      console.log($scope.issueDetail);
    }

    $scope.submit = function() {
      $scope.issueDetail.error = null;

      if (!$scope.issueDetail.actionType || !$scope.issueDetail.messageType) {
        return;
      }

      $scope.issueDetail.isDisabled = true;

      ScoreFactory.submitResponse($scope.issueDetail.number, $scope.issueDetail.actionType, $scope.issueDetail.messageType, $scope.issueDetail.customMessage).then(function(data){
        if (data.error) {
          $scope.issueDetail.error = data.error;
          $scope.issueDetail.isDisabled = false
          return;
        }

        if (data.issue_closed) {
          for (var x = 0; x < $scope.issue_data.length; x++) {
            if ($scope.issue_data[x].number == $scope.issueDetail.number) {
              $scope.issue_data.splice(x, 1);
              break;
            }
          }
        }

        $scope.issueDetail = null;
        console.log('submit response');
      });
    };

    ScoreFactory.fetchAll().then(function(data){
      $scope.isLoading = false;
      $scope.repo_data = data;
      $scope.issue_data = data.issues;
      $scope.errorMsg = data.error;
    });

})

.factory('ScoreFactory', function($http, $q){

  return {

    fetchAll: function() {
      var deferred = $q.defer();

      $http.get('/app/issue-scores')
        .success(function(data, status, headers, config) {
          deferred.resolve(data);
        })
        .error(function(data, status, headers, config) {
          deferred.reject(data);
        });
        return deferred.promise
    },

    submitResponse: function(number, actionType, messageType, customMessage) {
      var deferred = $q.defer();

      $http.post('/app/issue-response', {
        'number': number,
        'action_type': actionType,
        'message_type': messageType,
        'custom_message': customMessage
      })
        .success(function(data, status, headers, config) {
          deferred.resolve(data);
        })
        .error(function(data, status, headers, config) {
          deferred.reject(data);
        });
        return deferred.promise
    }

  }

})

.directive('stopEvent', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            element.bind('click', function (e) {
                e.stopPropagation();
            });
        }
    };
})

.filter('scoreData', function() {
  return function(scoreData) {
    var sortable = [];
    for (var n in scoreData) {
      sortable.push([n, scoreData[n]]);
    }
    sortable.sort(function(a, b) {return a[1] - b[1]}).reverse();

    var out = [];
    for (var x = 0; x < sortable.length; x++) {
      out.push(sortable[x][1] + ' - ' + sortable[x][0]);
    }

    return out.join('\n');
  };
})
