window['SimpleCometProxy'] = function() {
    var jsonp_cb = '_JSONP_comet_cb',
        min_delay = 100, timeout = 30000, since = 0, seq = 0;

    function create_jsonp_node(url) {
        var node = document.createElement('script');
        node.setAttribute('type', 'application/javascript');
        node.setAttribute('src', url);
        document.body.appendChild(node);

        return node;
    }

    function subscribe(url, cb, client_id) {
        var _url = url + '?since=' + encodeURIComponent(since) +
            '&t=' + (new Date).getTime() + '.' + seq;
        client_id && (_url += '&client_id=' + encodeURIComponent(client_id));
        var jsonp_node = create_jsonp_node(_url);
        var cancel_timer = setTimeout(function() {
            seq++;
            jsonp_node.parentNode.removeChild(jsonp_node);
            subscribe(url, cb, client_id);
        }, timeout);
        window[jsonp_cb] = function(resp) {
            clearTimeout(cancel_timer);
            jsonp_node.parentNode.removeChild(jsonp_node);
            if (resp.since >= since) {
                cb(resp);
                since = resp.last_id;
                setTimeout(function() {
                    subscribe(url, cb, client_id);
                }, min_delay);
            }
        }
    }

    return {
        'min_delay': min_delay,
        'timeout': timeout,
        'subscribe': subscribe
    };
}();

window['SimpleComet'] = function() {
    var frame_src = 'simple-comet-frame.html',
        queue = [];

    function create_comet_frame() {
        var node_comet_frame = document.createElement('iframe');
        node_comet_frame.setAttribute('src', frame_src);
        node_comet_frame.setAttribute('style', 'display:none');
        document.body.appendChild(node_comet_frame);
    }

    function comet_frame_ready_cb(simple_comet_proxy) {
        this.subscribe = simple_comet_proxy['subscribe'];
        for (var args; args = queue.shift();) {
            this.subscribe.apply(this, args);
        }
    }

    function subscribe(url, cb, client_id) {
        create_comet_frame && create_comet_frame();
        this.create_comet_frame = null;
        queue.push(arguments);
    }

    return {
        'frame_src': frame_src,
        'comet_frame_ready_cb': comet_frame_ready_cb,
        'subscribe': subscribe
    };
}();
