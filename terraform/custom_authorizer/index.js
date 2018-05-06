'use strict';

var lib = require('./lib');


// Lambda function index.handler - thin wrapper around lib.authenticate
module.exports.handler = function (event, context) {
  lib.authenticate(event, function (err, data) {
    if (err) {
      if (!err) context.fail("Unhandled error");
      context.fail("Unauthorized");
      console.log(err);
    }
    else context.succeed(data);

  });

};
