import PubSubChannel from './src/aux/pubsub.js';
import AnnotatorWebSocket from './src/aux/websocket.js';
import DocumentView from './src/document_view.js';
import PanelView from './src/panel.js';
import Annotator from './src/annotator.js';
import HistoryView from './src/history.js';
import {Popup, Tooltips} from './src/tooltips.js';

// Load all components
const websocket = AnnotatorWebSocket();
const channel = PubSubChannel.create();
const document_view = DocumentView({channel});
const panel_view = PanelView({channel});
const annotator = Annotator({channel});
const history_view = HistoryView({channel});
const popup = Popup({channel});
const tooltips = Tooltips({channel});

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

/*sub.publish('popup/render', {
	title: 'alex',
	subtitle: 'holaaaaaa',
	body: 'ajdjasjd asjd as dsv j esrdfvkj re adsvcneroijvdv eñdskfnv',
	x: '300px',
	y: '150px'
})
setTimeout(()=>sub.publish('popup/hide', {}), 3000);*/