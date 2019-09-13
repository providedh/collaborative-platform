// 'use strict';
//
// var m = require('mithril');
// var waterbutler = require('js/waterbutler');
// var annotator = require('./teicloseAnnotator.js');
//
// var CloseReadingWidget = {
//     controller: function(options) {
//         var self = this;
//         self.node = options.node;
//         self.file = options.file;
//
//         self.url = waterbutler.buildDownloadUrl(self.file.path, self.file.provider, self.node.id, {direct: true, mode: 'render', version: self.file.version});
//         self.loaded = false;
//         self.content = '';
//
//         self.socket = null;
//         self.first_entry = true;
//
//         createWebSocket();
//
//         function createWebSocket()
//         {
//             let wsPrefix = (window.location.protocol === 'https:') ? 'wss://' : 'ws://';
//
//             self.socket = new WebSocket(wsPrefix + window.location.host.split(':')[0] + ':8000' + '/websocket/' + self.node.id + '_' + self.file.id + '/');
//
//             if (self.socket.readyState === WebSocket.OPEN) {
//                 self.socket.onopen();
//             }
//
//             self.socket.onopen = function open() {
//                 console.log("WebSockets connection created.");
//             };
//
//             self.socket.onmessage = function message(event) {
//                 console.log("data from socket:" + event.data);
//
//                 if (self.first_entry)
//                 {
//                     m.startComputation();
//                     self.loaded = true;
//                     self.content = JSON.parse(event.data);
//                     m.endComputation();
//
//                     if (self.content.status === 200)
//                     {
//                         annotator.setup(self.content.xml_content);
//                         self.first_entry = false;
//                     }
//                 }
//                 else
//                 {
//                     self.content = JSON.parse(event.data);
//
//                     if (self.content.status === 200)
//                     {
//                         console.log('annotate - success < ', self.content);
//                         window.updateFile(self.content.xml_content);
//                     }
//                     else
//                     {
//                         console.log('annotate - failed < ', self.content);
//                     }
//                 }
//             };
//
//             setInterval(function () {
//             self.socket.send(JSON.stringify('heartbeat'));
//             }, 30000);
//         }
//
//         window.send = function (json)
//         {
//             self.socket.send(json);
//         };
//
//         let linkVersions = '/' + self.file.id + '/?show=revision&version=' + self.file.version;
//
//         if(self.file.provider === 'osfstorage'){
//             changeVersionHeader();
//         }
//
//         function changeVersionHeader(){
//             document.getElementById('versionLink').style.display = 'inline';
//             m.render(document.getElementById('versionLink'), m('a', {onclick: redirectToVersions}, document.getElementById('versionLink').innerHTML));
//         }
//
//         function redirectToVersions (){
//             window.location = linkVersions;
//             return false;
//         }
//
//         return self;
//     },
//     view: function(ctrl) {
//         return null;
//     }
// };
//
// module.exports = {
//     CloseReadingWidget: CloseReadingWidget
// };



self.loaded = false;
self.content = '';

self.socket = null;
self.first_entry = true;

createWebSocket();

function createWebSocket()
{
    let wsPrefix = (window.location.protocol === 'https:') ? 'wss://' : 'ws://';

    self.socket = new WebSocket(wsPrefix + window.location.host.split(':')[0] + '/ws/close_reading/' + self.project_id + '_' + self.file_id + '/');

    if (self.socket.readyState === WebSocket.OPEN) {
        self.socket.onopen();
    }

    self.socket.onopen = function open() {
        console.log("WebSockets connection created.");
    };

    self.socket.onmessage = function message(event) {
        console.log("data from socket:" + event.data);

        if (self.first_entry)
        {
            // m.startComputation();
            self.loaded = true;
            self.content = JSON.parse(event.data);
            // m.endComputation();

            if (self.content.status === 200)
            {
                setup(self.content.xml_content);
                self.first_entry = false;
            }
        }
        else
        {
            self.content = JSON.parse(event.data);

            if (self.content.status === 200)
            {
                console.log('annotate - success < ', self.content);
                window.updateFile(self.content.xml_content);
            }
            else
            {
                console.log('annotate - failed < ', self.content);
            }
        }
    };

    setInterval(function () {
    self.socket.send(JSON.stringify('heartbeat'));
    }, 30000);
}

window.send = function (json)
{
    self.socket.send(json);
};
