import PubSubChannel from './src/aux/pubsub.js';
import AnnotatorWebSocket from './src/aux/websocket.js';
import DocumentView from './src/document_view.js';

// Load all components
const channel = PubSubChannel.create();
const document_view = DocumentView({channel});

// Create suscriber for sending messages using
// the websocket
const sub = {};
channel.addToChannel(sub);
sub.subscribe('websocket/send', json=>AnnotatorWebSocket.send(json));
sub.subscribe('document/render', selection=>console.info('Document rendered.'));
sub.subscribe('document/selection', selection=>console.log(selection));

// Publish websocket updates
AnnotatorWebSocket.addCallback('onload', file=>sub.publish('document/load', file));
AnnotatorWebSocket.addCallback('onload', file=>console.log(file));
AnnotatorWebSocket.addCallback('onreload', file=>sub.publish('document/load', file));
AnnotatorWebSocket.addCallback('onreload', file=>console.log(file));

// Create websocket
AnnotatorWebSocket.create();
