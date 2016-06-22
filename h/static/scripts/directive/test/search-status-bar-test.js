'use strict';

var angular = require('angular');

var util = require('./util');
var unroll = require('../../test/util').unroll;

describe('searchStatusBar', function () {
  before(function () {
    angular.module('app', [])
      .directive('searchStatusBar', require('../search-status-bar'));
  });

  beforeEach(function () {
    angular.mock.module('app');
  });

  context('when there is a filter', function () {
    it('should display the filter count', function () {
      var elem = util.createDirective(document, 'searchStatusBar', {
        filterActive: true,
        filterMatchCount: 5
      });
      assert.include(elem[0].textContent, "5 search results");
    });
  });

  context('when there is a selection', function () {
    it('should display the "Show all annotations (2)" message when there are 2 annotations', function () {
      var msg = 'Show all annotations (2)';
      var elem = util.createDirective(document, 'searchStatusBar', {
        selectionCount: 1,
        totalAnnotations: 2,
        tabSelection: 'annotation',
      });
      var clearBtn = elem[0].querySelector('button');
      assert.include(clearBtn.textContent, msg);
    });
  });
});
