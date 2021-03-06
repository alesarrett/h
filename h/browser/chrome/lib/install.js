'use strict';

var HypothesisChromeExtension = require('./hypothesis-chrome-extension');

var browserExtension = new HypothesisChromeExtension({
  chromeTabs: chrome.tabs,
  chromeBrowserAction: chrome.browserAction,
  chromeStorage: chrome.storage,
  extensionURL: function (path) {
    return chrome.extension.getURL(path);
  },
  isAllowedFileSchemeAccess: function (fn) {
    return chrome.extension.isAllowedFileSchemeAccess(fn);
  },
});

browserExtension.listen(window);

if (chrome.runtime.onInstalled) {
  chrome.runtime.onInstalled.addListener(onInstalled);
}

// Respond to messages sent by the JavaScript from https://hpt.is.
// This is how it knows whether the user has this Chrome extension installed.
if (chrome.runtime.onMessageExternal) {
  chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {
      if (request.type === 'ping') {
        sendResponse({type: 'pong'});
      }
    }
  );
}

if (chrome.runtime.requestUpdateCheck) {
  chrome.runtime.requestUpdateCheck(function () {
    chrome.runtime.onUpdateAvailable.addListener(onUpdateAvailable);
  });
}

function onInstalled(installDetails) {
  // The install reason can be "install", "update", "chrome_update", or
  // "shared_module_update", see:
  //
  //   https://developer.chrome.com/extensions/runtime#type-OnInstalledReason
  //
  // If we were installed (rather than updated) then trigger a "firstRun" event,
  // passing in the details of the installed extension. See:
  //
  //   https://developer.chrome.com/extensions/management#method-getSelf
  //
  if (installDetails.reason === 'install') {
    chrome.management.getSelf(browserExtension.firstRun);
  }

  // We need this so that 3rd party cookie blocking does not kill us.
  // See https://github.com/hypothesis/h/issues/634 for more info.
  // This is intended to be a temporary fix only.
  var details = {
    primaryPattern: 'https://hypothes.is/*',
    setting: 'allow'
  };
  chrome.contentSettings.cookies.set(details);
  chrome.contentSettings.images.set(details);
  chrome.contentSettings.javascript.set(details);

  browserExtension.install();
}

function onUpdateAvailable() {
  chrome.runtime.reload();
}
