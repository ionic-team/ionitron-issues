angular.module('app', ['ui.router', 'ngGrid'])

.config(function($stateProvider, $urlRouterProvider) {

  $urlRouterProvider.otherwise("/");

  $stateProvider

    .state('home', {
      url: "/manage",
      templateUrl: "partials/home.html",
      controller: 'AppCtrl',
    })

    .state('issues', {
      url: "/",
      templateUrl: "partials/issues.html",
      controller: 'IssueCtrl',
    });


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

.controller('IssueCtrl', function($scope, ScoreFactory){

    $scope.isLoading = true;
    $scope.issue_data = [];

    $scope.gridOptions = {
        data: 'issue_data',
        sortInfo: { fields: ['score'], directions: ['desc']},
        columnDefs: [{field:'iid', displayName:'Issue #', width:'7%',
                      cellTemplate: '<div class="ngCellText" ng-class="col.colIndex()"><a href="http://github.com/driftyco/ionic/issues/{{row.getProperty(col.field)}}" target="_blank">#<span ng-cell-text>{{row.getProperty(col.field)}}</span></a></div>'},
                     {field:'score', displayName:'Score', width: '6%', cellFilter: 'number:0',
                      cellTemplate: '<div class="ngCellText" ng-class="col.colIndex()" title="{{row.getProperty(\'score_data\') | scoreData}}"><span ng-cell-text>{{row.getProperty(col.field)}}</span></div>'},
                     {field:'comments', displayName:'Comments', width: '7%', cellFilter: 'number:0'},
                     {field: 'created', displayName: 'Created', width: '10%', cellFilter: 'date:"MM/dd/yyyy"'},
                     {field: 'updated', displayName: 'Updated', width: '10%', cellFilter: 'date:"MM/dd/yyyy"'},
                     {field:'username', displayName:'User', width: '15%', cellTemplate: '<div class="ngCellText" ng-class="col.colIndex()"><img class="thumb" ng-src="{{row.getProperty(\'avatar\')}}"><a href="http://github.com/{{row.getProperty(col.field)}}" target="_blank"><span ng-cell-text>{{row.getProperty(col.field)}}</span></a></div>'},
                     {field: 'title', displayName: 'Title', width: '45%'},
                    ]
    }

    ScoreFactory.fetchAll().then(function(data){
      $scope.isLoading = false;
      $scope.issue_data = data.issues;
      $scope.errorMsg = data.error;
    });

})

.factory('ScoreFactory', function($http, $q){

  return {

    fetchAll: function(){
      deferred = $q.defer();

      $http.get('/api/issue-scores')
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
