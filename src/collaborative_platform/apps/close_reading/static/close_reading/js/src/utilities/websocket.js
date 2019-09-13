/* Module: WebSocket
 * Module implementing the websocket functionallity needed for 
 * retrieving and annotating TEI files.
 *
 * Callbacks can be added for each of the events that the websocket 
 * produces : onopen, onload, onreload, onsend
 * */

const AnnotatorWebSocket = function(){
    let loaded = false;
    let content = '';

    let socket = null;
    let first_entry = true;

    const callbacks = {
        onopen: [],
        onload: [],
        onreload: [],
        onsend: []
    };

    function _addCallback(event, callback){
        if(['onopen', 'onload', 'onreload', 'onsend'].includes(event) &&
                typeof(callback) == 'function'){
            callbacks[event].push(callback);
        }
    }

    function _createWebSocket()
    {
        let wsPrefix = (window.location.protocol === 'https:') ? 'wss://' : 'ws://';
        let port = '';

        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        {
            port = ':' + window.location.port
        }

        socket = new WebSocket(wsPrefix + window.location.host.split(':')[0] + port + '/ws/close_reading/' + project_id + '_' + file_id + '/');

        if (socket.readyState === WebSocket.OPEN) {
            socket.onopen();
        }

        socket.onopen = function open() {
            console.info("WebSockets connection created.");

            // Run any callbacks if any
            for(let callback of callbacks.onopen)
                callback();
        };

        socket.onmessage = function message(event) {
            //console.log("data from socket:" + event.data);
            if (first_entry)
            {
                // m.startComputation();
                loaded = true;
                content = JSON.parse(event.data);
                // m.endComputation();

                if (content.status === 200)
                {
                    first_entry = false;
                    
                    // Run any callbacks if any, with the contents retrieved
                    for(let callback of callbacks.onload)
                        callback(content.xml_content);
                }
            }
            else
            {
                content = JSON.parse(event.data);

                if (content.status === 200)
                {
                    //console.log('annotate - success < ', content);

                    // Run any callbacks if any, with the contents retrieved
                    for(let callback of callbacks.onreload)
                        callback(content.xml_content);
                }
                else
                {
                    console.log('annotate - failed < ', content);
                }
            }
        };

        setInterval(function () {
        socket.send(JSON.stringify('heartbeat'));
        }, 30000);
    }

    function _send(json)
    {
        socket.send(json);

        // Run any callbacks if any
        for(let callback of callbacks.onsend)
            callback();
    };

    return {
        version: 1,
        send: _send,
        addCallback:_addCallback,
        create: _createWebSocket
    }
}

export default AnnotatorWebSocket;