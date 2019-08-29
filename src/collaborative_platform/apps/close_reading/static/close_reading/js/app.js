import PubSubChannel from './src/aux/pubsub.js';
import AnnotatorWebSocket from './src/aux/websocket.js';
import DocumentView from './src/document_view.js';
import PanelView from './src/panel.js';
import Annotator from './src/annotator.js';
import HistoryView from './src/history.js';

// Load all components
const websocket = AnnotatorWebSocket();
const channel = PubSubChannel.create();
const document_view = DocumentView({channel});
const panel_view = PanelView({channel});
const annotator = Annotator({channel});
const history_view = HistoryView({channel});

// Create suscriber for sending messages using
// the websocket
const sub = {};
channel.addToChannel(sub);
sub.subscribe('websocket/send', json=>websocket.send(json));
sub.subscribe('document/render', selection=>console.info('Document rendered.'));

// Publish websocket updates
websocket.addCallback('onload', file=>sub.publish('document/load', file));
//AnnotatorWebSocket.addCallback('onload', file=>console.log(file));
websocket.addCallback('onreload', file=>sub.publish('document/load', file));

// Create websocket
websocket.create();
