'use strict';

// @ngInject
module.exports = function () {
  return {
    controller: function () {},
    restrict: 'E',
    scope: {
      filterActive: '<',
      filterMatchCount: '<',
      onClearSelection: '&',
      searchQuery: '<',
      selectionCount: '<',
      totalAnnotations: '<',
      totalNotes: '<',
      tabSelection: '<',
    },
    template: require('../../../templates/client/search_status_bar.html'),
  };
};
