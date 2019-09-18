
var m = (function app(window, undefined) {
	var OBJECT = "[object Object]", ARRAY = "[object Array]", STRING = "[object String]", FUNCTION = "function";
	var type = {}.toString;
	var parser = /(?:(^|#|\.)([^#\.\[\]]+))|(\[.+?\])/g, attrParser = /\[(.+?)(?:=("|'|)(.*?)\2)?\]/;
	var voidElements = /^(AREA|BASE|BR|COL|COMMAND|EMBED|HR|IMG|INPUT|KEYGEN|LINK|META|PARAM|SOURCE|TRACK|WBR)$/;
	var noop = function() {}

	// caching commonly used variables
	var $document, $location, $requestAnimationFrame, $cancelAnimationFrame;

	// self invoking function needed because of the way mocks work
	function initialize(window){
		$document = window.document;
		$location = window.location;
		$cancelAnimationFrame = window.cancelAnimationFrame || window.clearTimeout;
		$requestAnimationFrame = window.requestAnimationFrame || window.setTimeout;
	}

	initialize(window);


	/**
	 * @typedef {String} Tag
	 * A string that looks like -> div.classname#id[param=one][param2=two]
	 * Which describes a DOM node
	 */

	/**
	 *
	 * @param {Tag} The DOM node tag
	 * @param {Object=[]} optional key-value pairs to be mapped to DOM attrs
	 * @param {...mNode=[]} Zero or more Mithril child nodes. Can be an array, or splat (optional)
	 *
	 */
	function m() {
		var args = [].slice.call(arguments);
		var hasAttrs = args[1] != null && type.call(args[1]) === OBJECT && !("tag" in args[1] || "view" in args[1]) && !("subtree" in args[1]);
		var attrs = hasAttrs ? args[1] : {};
		var classAttrName = "class" in attrs ? "class" : "className";
		var cell = {tag: "div", attrs: {}};
		var match, classes = [];
		if (type.call(args[0]) != STRING) throw new Error("selector in m(selector, attrs, children) should be a string")
		while (match = parser.exec(args[0])) {
			if (match[1] === "" && match[2]) cell.tag = match[2];
			else if (match[1] === "#") cell.attrs.id = match[2];
			else if (match[1] === ".") classes.push(match[2]);
			else if (match[3][0] === "[") {
				var pair = attrParser.exec(match[3]);
				cell.attrs[pair[1]] = pair[3] || (pair[2] ? "" :true)
			}
		}

		var children = hasAttrs ? args.slice(2) : args.slice(1);
		if (children.length === 1 && type.call(children[0]) === ARRAY) {
			cell.children = children[0]
		}
		else {
			cell.children = children
		}
		
		for (var attrName in attrs) {
			if (attrs.hasOwnProperty(attrName)) {
				if (attrName === classAttrName && attrs[attrName] != null && attrs[attrName] !== "") {
					classes.push(attrs[attrName])
					cell.attrs[attrName] = "" //create key in correct iteration order
				}
				else cell.attrs[attrName] = attrs[attrName]
			}
		}
		if (classes.length > 0) cell.attrs[classAttrName] = classes.join(" ");
		
		return cell
	}
	function build(parentElement, parentTag, parentCache, parentIndex, data, cached, shouldReattach, index, editable, namespace, configs) {
		//`build` is a recursive function that manages creation/diffing/removal of DOM elements based on comparison between `data` and `cached`
		//the diff algorithm can be summarized as this:
		//1 - compare `data` and `cached`
		//2 - if they are different, copy `data` to `cached` and update the DOM based on what the difference is
		//3 - recursively apply this algorithm for every array and for the children of every virtual element

		//the `cached` data structure is essentially the same as the previous redraw's `data` data structure, with a few additions:
		//- `cached` always has a property called `nodes`, which is a list of DOM elements that correspond to the data represented by the respective virtual element
		//- in order to support attaching `nodes` as a property of `cached`, `cached` is *always* a non-primitive object, i.e. if the data was a string, then cached is a String instance. If data was `null` or `undefined`, cached is `new String("")`
		//- `cached also has a `configContext` property, which is the state storage object exposed by config(element, isInitialized, context)
		//- when `cached` is an Object, it represents a virtual element; when it's an Array, it represents a list of elements; when it's a String, Number or Boolean, it represents a text node

		//`parentElement` is a DOM element used for W3C DOM API calls
		//`parentTag` is only used for handling a corner case for textarea values
		//`parentCache` is used to remove nodes in some multi-node cases
		//`parentIndex` and `index` are used to figure out the offset of nodes. They're artifacts from before arrays started being flattened and are likely refactorable
		//`data` and `cached` are, respectively, the new and old nodes being diffed
		//`shouldReattach` is a flag indicating whether a parent node was recreated (if so, and if this node is reused, then this node must reattach itself to the new parent)
		//`editable` is a flag that indicates whether an ancestor is contenteditable
		//`namespace` indicates the closest HTML namespace as it cascades down from an ancestor
		//`configs` is a list of config functions to run after the topmost `build` call finishes running

		//there's logic that relies on the assumption that null and undefined data are equivalent to empty strings
		//- this prevents lifecycle surprises from procedural helpers that mix implicit and explicit return statements (e.g. function foo() {if (cond) return m("div")}
		//- it simplifies diffing code
		//data.toString() might throw or return null if data is the return value of Console.log in Firefox (behavior depends on version)
		try {if (data == null || data.toString() == null) data = "";} catch (e) {data = ""}
		if (data.subtree === "retain") return cached;
		var cachedType = type.call(cached), dataType = type.call(data);
		if (cached == null || cachedType !== dataType) {
			if (cached != null) {
				if (parentCache && parentCache.nodes) {
					var offset = index - parentIndex;
					var end = offset + (dataType === ARRAY ? data : cached.nodes).length;
					clear(parentCache.nodes.slice(offset, end), parentCache.slice(offset, end))
				}
				else if (cached.nodes) clear(cached.nodes, cached)
			}
			cached = new data.constructor;
			if (cached.tag) cached = {}; //if constructor creates a virtual dom element, use a blank object as the base cached node instead of copying the virtual el (#277)
			cached.nodes = []
		}

		if (dataType === ARRAY) {
			//recursively flatten array
			for (var i = 0, len = data.length; i < len; i++) {
				if (type.call(data[i]) === ARRAY) {
					data = data.concat.apply([], data);
					i-- //check current index again and flatten until there are no more nested arrays at that index
					len = data.length
				}
			}
			
			var nodes = [], intact = cached.length === data.length, subArrayCount = 0;

			//keys algorithm: sort elements without recreating them if keys are present
			//1) create a map of all existing keys, and mark all for deletion
			//2) add new keys to map and mark them for addition
			//3) if key exists in new list, change action from deletion to a move
			//4) for each key, handle its corresponding action as marked in previous steps
			var DELETION = 1, INSERTION = 2 , MOVE = 3;
			var existing = {}, shouldMaintainIdentities = false;
			for (var i = 0; i < cached.length; i++) {
				if (cached[i] && cached[i].attrs && cached[i].attrs.key != null) {
					shouldMaintainIdentities = true;
					existing[cached[i].attrs.key] = {action: DELETION, index: i}
				}
			}
			
			var guid = 0
			for (var i = 0, len = data.length; i < len; i++) {
				if (data[i] && data[i].attrs && data[i].attrs.key != null) {
					for (var j = 0, len = data.length; j < len; j++) {
						if (data[j] && data[j].attrs && data[j].attrs.key == null) data[j].attrs.key = "__mithril__" + guid++
					}
					break
				}
			}
			
			if (shouldMaintainIdentities) {
				var keysDiffer = false
				if (data.length != cached.length) keysDiffer = true
				else for (var i = 0, cachedCell, dataCell; cachedCell = cached[i], dataCell = data[i]; i++) {
					if (cachedCell.attrs && dataCell.attrs && cachedCell.attrs.key != dataCell.attrs.key) {
						keysDiffer = true
						break
					}
				}
				
				if (keysDiffer) {
					for (var i = 0, len = data.length; i < len; i++) {
						if (data[i] && data[i].attrs) {
							if (data[i].attrs.key != null) {
								var key = data[i].attrs.key;
								if (!existing[key]) existing[key] = {action: INSERTION, index: i};
								else existing[key] = {
									action: MOVE,
									index: i,
									from: existing[key].index,
									element: cached.nodes[existing[key].index] || $document.createElement("div")
								}
							}
						}
					}
					var actions = []
					for (var prop in existing) actions.push(existing[prop])
					var changes = actions.sort(sortChanges);
					var newCached = new Array(cached.length)
					newCached.nodes = cached.nodes.slice()

					for (var i = 0, change; change = changes[i]; i++) {
						if (change.action === DELETION) {
							clear(cached[change.index].nodes, cached[change.index]);
							newCached.splice(change.index, 1)
						}
						if (change.action === INSERTION) {
							var dummy = $document.createElement("div");
							dummy.key = data[change.index].attrs.key;
							parentElement.insertBefore(dummy, parentElement.childNodes[change.index] || null);
							newCached.splice(change.index, 0, {attrs: {key: data[change.index].attrs.key}, nodes: [dummy]})
							newCached.nodes[change.index] = dummy
						}

						if (change.action === MOVE) {
							if (parentElement.childNodes[change.index] !== change.element && change.element !== null) {
								parentElement.insertBefore(change.element, parentElement.childNodes[change.index] || null)
							}
							newCached[change.index] = cached[change.from]
							newCached.nodes[change.index] = change.element
						}
					}
					cached = newCached;
				}
			}
			//end key algorithm

			for (var i = 0, cacheCount = 0, len = data.length; i < len; i++) {
				//diff each item in the array
				var item = build(parentElement, parentTag, cached, index, data[i], cached[cacheCount], shouldReattach, index + subArrayCount || subArrayCount, editable, namespace, configs);
				if (item === undefined) continue;
				if (!item.nodes.intact) intact = false;
				if (item.$trusted) {
					//fix offset of next element if item was a trusted string w/ more than one html element
					//the first clause in the regexp matches elements
					//the second clause (after the pipe) matches text nodes
					subArrayCount += (item.match(/<[^\/]|\>\s*[^<]/g) || [0]).length
				}
				else subArrayCount += type.call(item) === ARRAY ? item.length : 1;
				cached[cacheCount++] = item
			}
			if (!intact) {
				//diff the array itself
				
				//update the list of DOM nodes by collecting the nodes from each item
				for (var i = 0, len = data.length; i < len; i++) {
					if (cached[i] != null) nodes.push.apply(nodes, cached[i].nodes)
				}
				//remove items from the end of the array if the new array is shorter than the old one
				//if errors ever happen here, the issue is most likely a bug in the construction of the `cached` data structure somewhere earlier in the program
				for (var i = 0, node; node = cached.nodes[i]; i++) {
					if (node.parentNode != null && nodes.indexOf(node) < 0) clear([node], [cached[i]])
				}
				if (data.length < cached.length) cached.length = data.length;
				cached.nodes = nodes
			}
		}
		else if (data != null && dataType === OBJECT) {
			var views = [], controllers = []
			while (data.view) {
				var view = data.view.$original || data.view
				var controllerIndex = m.redraw.strategy() == "diff" && cached.views ? cached.views.indexOf(view) : -1
				var controller = controllerIndex > -1 ? cached.controllers[controllerIndex] : new (data.controller || noop)
				var key = data && data.attrs && data.attrs.key
				data = pendingRequests == 0 || (cached && cached.controllers && cached.controllers.indexOf(controller) > -1) ? data.view(controller) : {tag: "placeholder"}
				if (data.subtree === "retain") return cached;
				if (key) {
					if (!data.attrs) data.attrs = {}
					data.attrs.key = key
				}
				if (controller.onunload) unloaders.push({controller: controller, handler: controller.onunload})
				views.push(view)
				controllers.push(controller)
			}
			if (!data.tag && controllers.length) throw new Error("Component template must return a virtual element, not an array, string, etc.")
			if (!data.attrs) data.attrs = {};
			if (!cached.attrs) cached.attrs = {};

			var dataAttrKeys = Object.keys(data.attrs)
			var hasKeys = dataAttrKeys.length > ("key" in data.attrs ? 1 : 0)
			//if an element is different enough from the one in cache, recreate it
			if (data.tag != cached.tag || dataAttrKeys.sort().join() != Object.keys(cached.attrs).sort().join() || data.attrs.id != cached.attrs.id || data.attrs.key != cached.attrs.key || (m.redraw.strategy() == "all" && (!cached.configContext || cached.configContext.retain !== true)) || (m.redraw.strategy() == "diff" && cached.configContext && cached.configContext.retain === false)) {
				if (cached.nodes.length) clear(cached.nodes);
				if (cached.configContext && typeof cached.configContext.onunload === FUNCTION) cached.configContext.onunload()
				if (cached.controllers) {
					for (var i = 0, controller; controller = cached.controllers[i]; i++) {
						if (typeof controller.onunload === FUNCTION) controller.onunload({preventDefault: noop})
					}
				}
			}
			if (type.call(data.tag) != STRING) return;

			var node, isNew = cached.nodes.length === 0;
			if (data.attrs.xmlns) namespace = data.attrs.xmlns;
			else if (data.tag === "svg") namespace = "http://www.w3.org/2000/svg";
			else if (data.tag === "math") namespace = "http://www.w3.org/1998/Math/MathML";
			
			if (isNew) {
				if (data.attrs.is) node = namespace === undefined ? $document.createElement(data.tag, data.attrs.is) : $document.createElementNS(namespace, data.tag, data.attrs.is);
				else node = namespace === undefined ? $document.createElement(data.tag) : $document.createElementNS(namespace, data.tag);
				cached = {
					tag: data.tag,
					//set attributes first, then create children
					attrs: hasKeys ? setAttributes(node, data.tag, data.attrs, {}, namespace) : data.attrs,
					children: data.children != null && data.children.length > 0 ?
						build(node, data.tag, undefined, undefined, data.children, cached.children, true, 0, data.attrs.contenteditable ? node : editable, namespace, configs) :
						data.children,
					nodes: [node]
				};
				if (controllers.length) {
					cached.views = views
					cached.controllers = controllers
					for (var i = 0, controller; controller = controllers[i]; i++) {
						if (controller.onunload && controller.onunload.$old) controller.onunload = controller.onunload.$old
						if (pendingRequests && controller.onunload) {
							var onunload = controller.onunload
							controller.onunload = noop
							controller.onunload.$old = onunload
						}
					}
				}
				
				if (cached.children && !cached.children.nodes) cached.children.nodes = [];
				//edge case: setting value on <select> doesn't work before children exist, so set it again after children have been created
				if (data.tag === "select" && "value" in data.attrs) setAttributes(node, data.tag, {value: data.attrs.value}, {}, namespace);
				parentElement.insertBefore(node, parentElement.childNodes[index] || null)
			}
			else {
				node = cached.nodes[0];
				if (hasKeys) setAttributes(node, data.tag, data.attrs, cached.attrs, namespace);
				cached.children = build(node, data.tag, undefined, undefined, data.children, cached.children, false, 0, data.attrs.contenteditable ? node : editable, namespace, configs);
				cached.nodes.intact = true;
				if (controllers.length) {
					cached.views = views
					cached.controllers = controllers
				}
				if (shouldReattach === true && node != null) parentElement.insertBefore(node, parentElement.childNodes[index] || null)
			}
			//schedule configs to be called. They are called after `build` finishes running
			if (typeof data.attrs["config"] === FUNCTION) {
				var context = cached.configContext = cached.configContext || {};

				// bind
				var callback = function(data, args) {
					return function() {
						return data.attrs["config"].apply(data, args)
					}
				};
				configs.push(callback(data, [node, !isNew, context, cached]))
			}
		}
		else if (typeof data != FUNCTION) {
			//handle text nodes
			var nodes;
			if (cached.nodes.length === 0) {
				if (data.$trusted) {
					nodes = injectHTML(parentElement, index, data)
				}
				else {
					nodes = [$document.createTextNode(data)];
					if (!parentElement.nodeName.match(voidElements)) parentElement.insertBefore(nodes[0], parentElement.childNodes[index] || null)
				}
				cached = "string number boolean".indexOf(typeof data) > -1 ? new data.constructor(data) : data;
				cached.nodes = nodes
			}
			else if (cached.valueOf() !== data.valueOf() || shouldReattach === true) {
				nodes = cached.nodes;
				if (!editable || editable !== $document.activeElement) {
					if (data.$trusted) {
						clear(nodes, cached);
						nodes = injectHTML(parentElement, index, data)
					}
					else {
						//corner case: replacing the nodeValue of a text node that is a child of a textarea/contenteditable doesn't work
						//we need to update the value property of the parent textarea or the innerHTML of the contenteditable element instead
						if (parentTag === "textarea") parentElement.value = data;
						else if (editable) editable.innerHTML = data;
						else {
							if (nodes[0].nodeType === 1 || nodes.length > 1) { //was a trusted string
								clear(cached.nodes, cached);
								nodes = [$document.createTextNode(data)]
							}
							parentElement.insertBefore(nodes[0], parentElement.childNodes[index] || null);
							nodes[0].nodeValue = data
						}
					}
				}
				cached = new data.constructor(data);
				cached.nodes = nodes
			}
			else cached.nodes.intact = true
		}

		return cached
	}
	function sortChanges(a, b) {return a.action - b.action || a.index - b.index}
	function setAttributes(node, tag, dataAttrs, cachedAttrs, namespace) {
		for (var attrName in dataAttrs) {
			var dataAttr = dataAttrs[attrName];
			var cachedAttr = cachedAttrs[attrName];
			if (!(attrName in cachedAttrs) || (cachedAttr !== dataAttr)) {
				cachedAttrs[attrName] = dataAttr;
				try {
					//`config` isn't a real attributes, so ignore it
					if (attrName === "config" || attrName == "key") continue;
					//hook event handlers to the auto-redrawing system
					else if (typeof dataAttr === FUNCTION && attrName.indexOf("on") === 0) {
						node[attrName] = autoredraw(dataAttr, node)
					}
					//handle `style: {...}`
					else if (attrName === "style" && dataAttr != null && type.call(dataAttr) === OBJECT) {
						for (var rule in dataAttr) {
							if (cachedAttr == null || cachedAttr[rule] !== dataAttr[rule]) node.style[rule] = dataAttr[rule]
						}
						for (var rule in cachedAttr) {
							if (!(rule in dataAttr)) node.style[rule] = ""
						}
					}
					//handle SVG
					else if (namespace != null) {
						if (attrName === "href") node.setAttributeNS("http://www.w3.org/1999/xlink", "href", dataAttr);
						else if (attrName === "className") node.setAttribute("class", dataAttr);
						else node.setAttribute(attrName, dataAttr)
					}
					//handle cases that are properties (but ignore cases where we should use setAttribute instead)
					//- list and form are typically used as strings, but are DOM element references in js
					//- when using CSS selectors (e.g. `m("[style='']")`), style is used as a string, but it's an object in js
					else if (attrName in node && !(attrName === "list" || attrName === "style" || attrName === "form" || attrName === "type" || attrName === "width" || attrName === "height")) {
						//#348 don't set the value if not needed otherwise cursor placement breaks in Chrome
						if (tag !== "input" || node[attrName] !== dataAttr) node[attrName] = dataAttr
					}
					else node.setAttribute(attrName, dataAttr)
				}
				catch (e) {
					//swallow IE's invalid argument errors to mimic HTML's fallback-to-doing-nothing-on-invalid-attributes behavior
					if (e.message.indexOf("Invalid argument") < 0) throw e
				}
			}
			//#348 dataAttr may not be a string, so use loose comparison (double equal) instead of strict (triple equal)
			else if (attrName === "value" && tag === "input" && node.value != dataAttr) {
				node.value = dataAttr
			}
		}
		return cachedAttrs
	}
	function clear(nodes, cached) {
		for (var i = nodes.length - 1; i > -1; i--) {
			if (nodes[i] && nodes[i].parentNode) {
				try {nodes[i].parentNode.removeChild(nodes[i])}
				catch (e) {} //ignore if this fails due to order of events (see http://stackoverflow.com/questions/21926083/failed-to-execute-removechild-on-node)
				cached = [].concat(cached);
				if (cached[i]) unload(cached[i])
			}
		}
		if (nodes.length != 0) nodes.length = 0
	}
	function unload(cached) {
		if (cached.configContext && typeof cached.configContext.onunload === FUNCTION) {
			cached.configContext.onunload();
			cached.configContext.onunload = null
		}
		if (cached.controllers) {
			for (var i = 0, controller; controller = cached.controllers[i]; i++) {
				if (typeof controller.onunload === FUNCTION) controller.onunload({preventDefault: noop});
			}
		}
		if (cached.children) {
			if (type.call(cached.children) === ARRAY) {
				for (var i = 0, child; child = cached.children[i]; i++) unload(child)
			}
			else if (cached.children.tag) unload(cached.children)
		}
	}
	function injectHTML(parentElement, index, data) {
		var nextSibling = parentElement.childNodes[index];
		if (nextSibling) {
			var isElement = nextSibling.nodeType != 1;
			var placeholder = $document.createElement("span");
			if (isElement) {
				parentElement.insertBefore(placeholder, nextSibling || null);
				placeholder.insertAdjacentHTML("beforebegin", data);
				parentElement.removeChild(placeholder)
			}
			else nextSibling.insertAdjacentHTML("beforebegin", data)
		}
		else parentElement.insertAdjacentHTML("beforeend", data);
		var nodes = [];
		while (parentElement.childNodes[index] !== nextSibling) {
			nodes.push(parentElement.childNodes[index]);
			index++
		}
		return nodes
	}
	function autoredraw(callback, object) {
		return function(e) {
			e = e || event;
			m.redraw.strategy("diff");
			m.startComputation();
			try {return callback.call(object, e)}
			finally {
				endFirstComputation()
			}
		}
	}

	var html;
	var documentNode = {
		appendChild: function(node) {
			if (html === undefined) html = $document.createElement("html");
			if ($document.documentElement && $document.documentElement !== node) {
				$document.replaceChild(node, $document.documentElement)
			}
			else $document.appendChild(node);
			this.childNodes = $document.childNodes
		},
		insertBefore: function(node) {
			this.appendChild(node)
		},
		childNodes: []
	};
	var nodeCache = [], cellCache = {};
	m.render = function(root, cell, forceRecreation) {
		var configs = [];
		if (!root) throw new Error("Ensure the DOM element being passed to m.route/m.mount/m.render is not undefined.");
		var id = getCellCacheKey(root);
		var isDocumentRoot = root === $document;
		var node = isDocumentRoot || root === $document.documentElement ? documentNode : root;
		if (isDocumentRoot && cell.tag != "html") cell = {tag: "html", attrs: {}, children: cell};
		if (cellCache[id] === undefined) clear(node.childNodes);
		if (forceRecreation === true) reset(root);
		cellCache[id] = build(node, null, undefined, undefined, cell, cellCache[id], false, 0, null, undefined, configs);
		for (var i = 0, len = configs.length; i < len; i++) configs[i]()
	};
	function getCellCacheKey(element) {
		var index = nodeCache.indexOf(element);
		return index < 0 ? nodeCache.push(element) - 1 : index
	}

	m.trust = function(value) {
		value = new String(value);
		value.$trusted = true;
		return value
	};

	function gettersetter(store) {
		var prop = function() {
			if (arguments.length) store = arguments[0];
			return store
		};

		prop.toJSON = function() {
			return store
		};

		return prop
	}

	m.prop = function (store) {
		//note: using non-strict equality check here because we're checking if store is null OR undefined
		if (((store != null && type.call(store) === OBJECT) || typeof store === FUNCTION) && typeof store.then === FUNCTION) {
			return propify(store)
		}

		return gettersetter(store)
	};

	var roots = [], components = [], controllers = [], lastRedrawId = null, lastRedrawCallTime = 0, computePreRedrawHook = null, computePostRedrawHook = null, prevented = false, topComponent, unloaders = [];
	var FRAME_BUDGET = 16; //60 frames per second = 1 call per 16 ms
	function parameterize(component, args) {
		var controller = function() {
			return (component.controller || noop).apply(this, args) || this
		}
		var view = function(ctrl) {
			if (arguments.length > 1) args = args.concat([].slice.call(arguments, 1))
			return component.view.apply(component, args ? [ctrl].concat(args) : [ctrl])
		}
		view.$original = component.view
		var output = {controller: controller, view: view}
		if (args[0] && args[0].key != null) output.attrs = {key: args[0].key}
		return output
	}
	m.component = function(component) {
		return parameterize(component, [].slice.call(arguments, 1))
	}
	m.mount = m.module = function(root, component) {
		if (!root) throw new Error("Please ensure the DOM element exists before rendering a template into it.");
		var index = roots.indexOf(root);
		if (index < 0) index = roots.length;
		
		var isPrevented = false;
		var event = {preventDefault: function() {
			isPrevented = true;
			computePreRedrawHook = computePostRedrawHook = null;
		}};
		for (var i = 0, unloader; unloader = unloaders[i]; i++) {
			unloader.handler.call(unloader.controller, event)
			unloader.controller.onunload = null
		}
		if (isPrevented) {
			for (var i = 0, unloader; unloader = unloaders[i]; i++) unloader.controller.onunload = unloader.handler
		}
		else unloaders = []
		
		if (controllers[index] && typeof controllers[index].onunload === FUNCTION) {
			controllers[index].onunload(event)
		}
		
		if (!isPrevented) {
			m.redraw.strategy("all");
			m.startComputation();
			roots[index] = root;
			if (arguments.length > 2) component = subcomponent(component, [].slice.call(arguments, 2))
			var currentComponent = topComponent = component = component || {controller: function() {}};
			var constructor = component.controller || noop
			var controller = new constructor;
			//controllers may call m.mount recursively (via m.route redirects, for example)
			//this conditional ensures only the last recursive m.mount call is applied
			if (currentComponent === topComponent) {
				controllers[index] = controller;
				components[index] = component
			}
			endFirstComputation();
			return controllers[index]
		}
	};
	var redrawing = false
	m.redraw = function(force) {
		if (redrawing) return
		redrawing = true
		//lastRedrawId is a positive number if a second redraw is requested before the next animation frame
		//lastRedrawID is null if it's the first redraw and not an event handler
		if (lastRedrawId && force !== true) {
			//when setTimeout: only reschedule redraw if time between now and previous redraw is bigger than a frame, otherwise keep currently scheduled timeout
			//when rAF: always reschedule redraw
			if ($requestAnimationFrame === window.requestAnimationFrame || new Date - lastRedrawCallTime > FRAME_BUDGET) {
				if (lastRedrawId > 0) $cancelAnimationFrame(lastRedrawId);
				lastRedrawId = $requestAnimationFrame(redraw, FRAME_BUDGET)
			}
		}
		else {
			redraw();
			lastRedrawId = $requestAnimationFrame(function() {lastRedrawId = null}, FRAME_BUDGET)
		}
		redrawing = false
	};
	m.redraw.strategy = m.prop();
	function redraw() {
		if (computePreRedrawHook) {
			computePreRedrawHook()
			computePreRedrawHook = null
		}
		for (var i = 0, root; root = roots[i]; i++) {
			if (controllers[i]) {
				var args = components[i].controller && components[i].controller.$$args ? [controllers[i]].concat(components[i].controller.$$args) : [controllers[i]]
				m.render(root, components[i].view ? components[i].view(controllers[i], args) : "")
			}
		}
		//after rendering within a routed context, we need to scroll back to the top, and fetch the document title for history.pushState
		if (computePostRedrawHook) {
			computePostRedrawHook();
			computePostRedrawHook = null
		}
		lastRedrawId = null;
		lastRedrawCallTime = new Date;
		m.redraw.strategy("diff")
	}

	var pendingRequests = 0;
	m.startComputation = function() {pendingRequests++};
	m.endComputation = function() {
		pendingRequests = Math.max(pendingRequests - 1, 0);
		if (pendingRequests === 0) m.redraw()
	};
	var endFirstComputation = function() {
		if (m.redraw.strategy() == "none") {
			pendingRequests--
			m.redraw.strategy("diff")
		}
		else m.endComputation();
	}

	m.withAttr = function(prop, withAttrCallback) {
		return function(e) {
			e = e || event;
			var currentTarget = e.currentTarget || this;
			withAttrCallback(prop in currentTarget ? currentTarget[prop] : currentTarget.getAttribute(prop))
		}
	};

	//routing
	var modes = {pathname: "", hash: "#", search: "?"};
	var redirect = noop, routeParams, currentRoute, isDefaultRoute = false;
	m.route = function() {
		//m.route()
		if (arguments.length === 0) return currentRoute;
		//m.route(el, defaultRoute, routes)
		else if (arguments.length === 3 && type.call(arguments[1]) === STRING) {
			var root = arguments[0], defaultRoute = arguments[1], router = arguments[2];
			redirect = function(source) {
				var path = currentRoute = normalizeRoute(source);
				if (!routeByValue(root, router, path)) {
					if (isDefaultRoute) throw new Error("Ensure the default route matches one of the routes defined in m.route")
					isDefaultRoute = true
					m.route(defaultRoute, true)
					isDefaultRoute = false
				}
			};
			var listener = m.route.mode === "hash" ? "onhashchange" : "onpopstate";
			window[listener] = function() {
				var path = $location[m.route.mode]
				if (m.route.mode === "pathname") path += $location.search
				if (currentRoute != normalizeRoute(path)) {
					redirect(path)
				}
			};
			computePreRedrawHook = setScroll;
			window[listener]()
		}
		//config: m.route
		else if (arguments[0].addEventListener || arguments[0].attachEvent) {
			var element = arguments[0];
			var isInitialized = arguments[1];
			var context = arguments[2];
			var vdom = arguments[3];
			element.href = (m.route.mode !== 'pathname' ? $location.pathname : '') + modes[m.route.mode] + vdom.attrs.href;
			if (element.addEventListener) {
				element.removeEventListener("click", routeUnobtrusive);
				element.addEventListener("click", routeUnobtrusive)
			}
			else {
				element.detachEvent("onclick", routeUnobtrusive);
				element.attachEvent("onclick", routeUnobtrusive)
			}
		}
		//m.route(route, params, shouldReplaceHistoryEntry)
		else if (type.call(arguments[0]) === STRING) {
			var oldRoute = currentRoute;
			currentRoute = arguments[0];
			var args = arguments[1] || {}
			var queryIndex = currentRoute.indexOf("?")
			var params = queryIndex > -1 ? parseQueryString(currentRoute.slice(queryIndex + 1)) : {}
			for (var i in args) params[i] = args[i]
			var querystring = buildQueryString(params)
			var currentPath = queryIndex > -1 ? currentRoute.slice(0, queryIndex) : currentRoute
			if (querystring) currentRoute = currentPath + (currentPath.indexOf("?") === -1 ? "?" : "&") + querystring;

			var shouldReplaceHistoryEntry = (arguments.length === 3 ? arguments[2] : arguments[1]) === true || oldRoute === arguments[0];

			if (window.history.pushState) {
				computePreRedrawHook = setScroll
				computePostRedrawHook = function() {
					window.history[shouldReplaceHistoryEntry ? "replaceState" : "pushState"](null, $document.title, modes[m.route.mode] + currentRoute);
				};
				redirect(modes[m.route.mode] + currentRoute)
			}
			else {
				$location[m.route.mode] = currentRoute
				redirect(modes[m.route.mode] + currentRoute)
			}
		}
	};
	m.route.param = function(key) {
		if (!routeParams) throw new Error("You must call m.route(element, defaultRoute, routes) before calling m.route.param()")
		return routeParams[key]
	};
	m.route.mode = "search";
	function normalizeRoute(route) {
		return route.slice(modes[m.route.mode].length)
	}
	function routeByValue(root, router, path) {
		routeParams = {};

		var queryStart = path.indexOf("?");
		if (queryStart !== -1) {
			routeParams = parseQueryString(path.substr(queryStart + 1, path.length));
			path = path.substr(0, queryStart)
		}

		// Get all routes and check if there's
		// an exact match for the current path
		var keys = Object.keys(router);
		var index = keys.indexOf(path);
		if(index !== -1){
			m.mount(root, router[keys [index]]);
			return true;
		}

		for (var route in router) {
			if (route === path) {
				m.mount(root, router[route]);
				return true
			}

			var matcher = new RegExp("^" + route.replace(/:[^\/]+?\.{3}/g, "(.*?)").replace(/:[^\/]+/g, "([^\\/]+)") + "\/?$");

			if (matcher.test(path)) {
				path.replace(matcher, function() {
					var keys = route.match(/:[^\/]+/g) || [];
					var values = [].slice.call(arguments, 1, -2);
					for (var i = 0, len = keys.length; i < len; i++) routeParams[keys[i].replace(/:|\./g, "")] = decodeURIComponent(values[i])
					m.mount(root, router[route])
				});
				return true
			}
		}
	}
	function routeUnobtrusive(e) {
		e = e || event;
		if (e.ctrlKey || e.metaKey || e.which === 2) return;
		if (e.preventDefault) e.preventDefault();
		else e.returnValue = false;
		var currentTarget = e.currentTarget || e.srcElement;
		var args = m.route.mode === "pathname" && currentTarget.search ? parseQueryString(currentTarget.search.slice(1)) : {};
		while (currentTarget && currentTarget.nodeName.toUpperCase() != "A") currentTarget = currentTarget.parentNode
		m.route(currentTarget[m.route.mode].slice(modes[m.route.mode].length), args)
	}
	function setScroll() {
		if (m.route.mode != "hash" && $location.hash) $location.hash = $location.hash;
		else window.scrollTo(0, 0)
	}
	function buildQueryString(object, prefix) {
		var duplicates = {}
		var str = []
		for (var prop in object) {
			var key = prefix ? prefix + "[" + prop + "]" : prop
			var value = object[prop]
			var valueType = type.call(value)
			var pair = (value === null) ? encodeURIComponent(key) :
				valueType === OBJECT ? buildQueryString(value, key) :
				valueType === ARRAY ? value.reduce(function(memo, item) {
					if (!duplicates[key]) duplicates[key] = {}
					if (!duplicates[key][item]) {
						duplicates[key][item] = true
						return memo.concat(encodeURIComponent(key) + "=" + encodeURIComponent(item))
					}
					return memo
				}, []).join("&") :
				encodeURIComponent(key) + "=" + encodeURIComponent(value)
			if (value !== undefined) str.push(pair)
		}
		return str.join("&")
	}
	function parseQueryString(str) {
		if (str.charAt(0) === "?") str = str.substring(1);
		
		var pairs = str.split("&"), params = {};
		for (var i = 0, len = pairs.length; i < len; i++) {
			var pair = pairs[i].split("=");
			var key = decodeURIComponent(pair[0])
			var value = pair.length == 2 ? decodeURIComponent(pair[1]) : null
			if (params[key] != null) {
				if (type.call(params[key]) !== ARRAY) params[key] = [params[key]]
				params[key].push(value)
			}
			else params[key] = value
		}
		return params
	}
	m.route.buildQueryString = buildQueryString
	m.route.parseQueryString = parseQueryString
	
	function reset(root) {
		var cacheKey = getCellCacheKey(root);
		clear(root.childNodes, cellCache[cacheKey]);
		cellCache[cacheKey] = undefined
	}

	m.deferred = function () {
		var deferred = new Deferred();
		deferred.promise = propify(deferred.promise);
		return deferred
	};
	function propify(promise, initialValue) {
		var prop = m.prop(initialValue);
		promise.then(prop);
		prop.then = function(resolve, reject) {
			return propify(promise.then(resolve, reject), initialValue)
		};
		return prop
	}
	//Promiz.mithril.js | Zolmeister | MIT
	//a modified version of Promiz.js, which does not conform to Promises/A+ for two reasons:
	//1) `then` callbacks are called synchronously (because setTimeout is too slow, and the setImmediate polyfill is too big
	//2) throwing subclasses of Error cause the error to be bubbled up instead of triggering rejection (because the spec does not account for the important use case of default browser error handling, i.e. message w/ line number)
	function Deferred(successCallback, failureCallback) {
		var RESOLVING = 1, REJECTING = 2, RESOLVED = 3, REJECTED = 4;
		var self = this, state = 0, promiseValue = 0, next = [];

		self["promise"] = {};

		self["resolve"] = function(value) {
			if (!state) {
				promiseValue = value;
				state = RESOLVING;

				fire()
			}
			return this
		};

		self["reject"] = function(value) {
			if (!state) {
				promiseValue = value;
				state = REJECTING;

				fire()
			}
			return this
		};

		self.promise["then"] = function(successCallback, failureCallback) {
			var deferred = new Deferred(successCallback, failureCallback);
			if (state === RESOLVED) {
				deferred.resolve(promiseValue)
			}
			else if (state === REJECTED) {
				deferred.reject(promiseValue)
			}
			else {
				next.push(deferred)
			}
			return deferred.promise
		};

		function finish(type) {
			state = type || REJECTED;
			next.map(function(deferred) {
				state === RESOLVED && deferred.resolve(promiseValue) || deferred.reject(promiseValue)
			})
		}

		function thennable(then, successCallback, failureCallback, notThennableCallback) {
			if (((promiseValue != null && type.call(promiseValue) === OBJECT) || typeof promiseValue === FUNCTION) && typeof then === FUNCTION) {
				try {
					// count protects against abuse calls from spec checker
					var count = 0;
					then.call(promiseValue, function(value) {
						if (count++) return;
						promiseValue = value;
						successCallback()
					}, function (value) {
						if (count++) return;
						promiseValue = value;
						failureCallback()
					})
				}
				catch (e) {
					m.deferred.onerror(e);
					promiseValue = e;
					failureCallback()
				}
			} else {
				notThennableCallback()
			}
		}

		function fire() {
			// check if it's a thenable
			var then;
			try {
				then = promiseValue && promiseValue.then
			}
			catch (e) {
				m.deferred.onerror(e);
				promiseValue = e;
				state = REJECTING;
				return fire()
			}
			thennable(then, function() {
				state = RESOLVING;
				fire()
			}, function() {
				state = REJECTING;
				fire()
			}, function() {
				try {
					if (state === RESOLVING && typeof successCallback === FUNCTION) {
						promiseValue = successCallback(promiseValue)
					}
					else if (state === REJECTING && typeof failureCallback === "function") {
						promiseValue = failureCallback(promiseValue);
						state = RESOLVING
					}
				}
				catch (e) {
					m.deferred.onerror(e);
					promiseValue = e;
					return finish()
				}

				if (promiseValue === self) {
					promiseValue = TypeError();
					finish()
				}
				else {
					thennable(then, function () {
						finish(RESOLVED)
					}, finish, function () {
						finish(state === RESOLVING && RESOLVED)
					})
				}
			})
		}
	}
	m.deferred.onerror = function(e) {
		if (type.call(e) === "[object Error]" && !e.constructor.toString().match(/ Error/)) throw e
	};

	m.sync = function(args) {
		var method = "resolve";
		function synchronizer(pos, resolved) {
			return function(value) {
				results[pos] = value;
				if (!resolved) method = "reject";
				if (--outstanding === 0) {
					deferred.promise(results);
					deferred[method](results)
				}
				return value
			}
		}

		var deferred = m.deferred();
		var outstanding = args.length;
		var results = new Array(outstanding);
		if (args.length > 0) {
			for (var i = 0; i < args.length; i++) {
				args[i].then(synchronizer(i, true), synchronizer(i, false))
			}
		}
		else deferred.resolve([]);

		return deferred.promise
	};
	function identity(value) {return value}

	function ajax(options) {
		if (options.dataType && options.dataType.toLowerCase() === "jsonp") {
			var callbackKey = "mithril_callback_" + new Date().getTime() + "_" + (Math.round(Math.random() * 1e16)).toString(36);
			var script = $document.createElement("script");

			window[callbackKey] = function(resp) {
				script.parentNode.removeChild(script);
				options.onload({
					type: "load",
					target: {
						responseText: resp
					}
				});
				window[callbackKey] = undefined
			};

			script.onerror = function(e) {
				script.parentNode.removeChild(script);

				options.onerror({
					type: "error",
					target: {
						status: 500,
						responseText: JSON.stringify({error: "Error making jsonp request"})
					}
				});
				window[callbackKey] = undefined;

				return false
			};

			script.onload = function(e) {
				return false
			};

			script.src = options.url
				+ (options.url.indexOf("?") > 0 ? "&" : "?")
				+ (options.callbackKey ? options.callbackKey : "callback")
				+ "=" + callbackKey
				+ "&" + buildQueryString(options.data || {});
			$document.body.appendChild(script)
		}
		else {
			var xhr = new window.XMLHttpRequest;
			xhr.open(options.method, options.url, true, options.user, options.password);
			xhr.onreadystatechange = function() {
				if (xhr.readyState === 4) {
					if (xhr.status >= 200 && xhr.status < 300) options.onload({type: "load", target: xhr});
					else options.onerror({type: "error", target: xhr})
				}
			};
			if (options.serialize === JSON.stringify && options.data && options.method !== "GET") {
				xhr.setRequestHeader("Content-Type", "application/json; charset=utf-8")
			}
			if (options.deserialize === JSON.parse) {
				xhr.setRequestHeader("Accept", "application/json, text/*");
			}
			if (typeof options.config === FUNCTION) {
				var maybeXhr = options.config(xhr, options);
				if (maybeXhr != null) xhr = maybeXhr
			}

			var data = options.method === "GET" || !options.data ? "" : options.data
			if (data && (type.call(data) != STRING && data.constructor != window.FormData)) {
				throw "Request data should be either be a string or FormData. Check the `serialize` option in `m.request`";
			}
			xhr.send(data);
			return xhr
		}
	}
	function bindData(xhrOptions, data, serialize) {
		if (xhrOptions.method === "GET" && xhrOptions.dataType != "jsonp") {
			var prefix = xhrOptions.url.indexOf("?") < 0 ? "?" : "&";
			var querystring = buildQueryString(data);
			xhrOptions.url = xhrOptions.url + (querystring ? prefix + querystring : "")
		}
		else xhrOptions.data = serialize(data);
		return xhrOptions
	}
	function parameterizeUrl(url, data) {
		var tokens = url.match(/:[a-z]\w+/gi);
		if (tokens && data) {
			for (var i = 0; i < tokens.length; i++) {
				var key = tokens[i].slice(1);
				url = url.replace(tokens[i], data[key]);
				delete data[key]
			}
		}
		return url
	}

	m.request = function(xhrOptions) {
		if (xhrOptions.background !== true) m.startComputation();
		var deferred = new Deferred();
		var isJSONP = xhrOptions.dataType && xhrOptions.dataType.toLowerCase() === "jsonp";
		var serialize = xhrOptions.serialize = isJSONP ? identity : xhrOptions.serialize || JSON.stringify;
		var deserialize = xhrOptions.deserialize = isJSONP ? identity : xhrOptions.deserialize || JSON.parse;
		var extract = isJSONP ? function(jsonp) {return jsonp.responseText} : xhrOptions.extract || function(xhr) {
			return xhr.responseText.length === 0 && deserialize === JSON.parse ? null : xhr.responseText
		};
		xhrOptions.method = (xhrOptions.method || 'GET').toUpperCase();
		xhrOptions.url = parameterizeUrl(xhrOptions.url, xhrOptions.data);
		xhrOptions = bindData(xhrOptions, xhrOptions.data, serialize);
		xhrOptions.onload = xhrOptions.onerror = function(e) {
			try {
				e = e || event;
				var unwrap = (e.type === "load" ? xhrOptions.unwrapSuccess : xhrOptions.unwrapError) || identity;
				var response = unwrap(deserialize(extract(e.target, xhrOptions)), e.target);
				if (e.type === "load") {
					if (type.call(response) === ARRAY && xhrOptions.type) {
						for (var i = 0; i < response.length; i++) response[i] = new xhrOptions.type(response[i])
					}
					else if (xhrOptions.type) response = new xhrOptions.type(response)
				}
				deferred[e.type === "load" ? "resolve" : "reject"](response)
			}
			catch (e) {
				m.deferred.onerror(e);
				deferred.reject(e)
			}
			if (xhrOptions.background !== true) m.endComputation()
		};
		ajax(xhrOptions);
		deferred.promise = propify(deferred.promise, xhrOptions.initialValue);
		return deferred.promise
	};

	//testing API
	m.deps = function(mock) {
		initialize(window = mock || window);
		return window;
	};
	//for internal testing only, do not use `m.deps.factory`
	m.deps.factory = app;

	return m
})(typeof window != "undefined" ? window : {});

if (typeof module != "undefined" && module !== null && module.exports) module.exports = m;
else if (typeof define === "function" && define.amd) define(function() {return m});


;(function(){

/**
 * Require the module at `name`.
 *
 * @param {String} name
 * @return {Object} exports
 * @api public
 */

function require(name) {
  var module = require.modules[name];
  if (!module) throw new Error('failed to require "' + name + '"');

  if (!('exports' in module) && typeof module.definition === 'function') {
    module.client = module.component = true;
    module.definition.call(this, module.exports = {}, module);
    delete module.definition;
  }

  return module.exports;
}

/**
 * Registered modules.
 */

require.modules = {};

/**
 * Register module at `name` with callback `definition`.
 *
 * @param {String} name
 * @param {Function} definition
 * @api private
 */

require.register = function (name, definition) {
  require.modules[name] = {
    definition: definition
  };
};

/**
 * Define a module's exports immediately with `exports`.
 *
 * @param {String} name
 * @param {Generic} exports
 * @api private
 */

require.define = function (name, exports) {
  require.modules[name] = {
    exports: exports
  };
};
require.register("component~emitter@1.1.2", function (exports, module) {

/**
 * Expose `Emitter`.
 */

module.exports = Emitter;

/**
 * Initialize a new `Emitter`.
 *
 * @api public
 */

function Emitter(obj) {
  if (obj) return mixin(obj);
};

/**
 * Mixin the emitter properties.
 *
 * @param {Object} obj
 * @return {Object}
 * @api private
 */

function mixin(obj) {
  for (var key in Emitter.prototype) {
    obj[key] = Emitter.prototype[key];
  }
  return obj;
}

/**
 * Listen on the given `event` with `fn`.
 *
 * @param {String} event
 * @param {Function} fn
 * @return {Emitter}
 * @api public
 */

Emitter.prototype.on =
Emitter.prototype.addEventListener = function(event, fn){
  this._callbacks = this._callbacks || {};
  (this._callbacks[event] = this._callbacks[event] || [])
    .push(fn);
  return this;
};

/**
 * Adds an `event` listener that will be invoked a single
 * time then automatically removed.
 *
 * @param {String} event
 * @param {Function} fn
 * @return {Emitter}
 * @api public
 */

Emitter.prototype.once = function(event, fn){
  var self = this;
  this._callbacks = this._callbacks || {};

  function on() {
    self.off(event, on);
    fn.apply(this, arguments);
  }

  on.fn = fn;
  this.on(event, on);
  return this;
};

/**
 * Remove the given callback for `event` or all
 * registered callbacks.
 *
 * @param {String} event
 * @param {Function} fn
 * @return {Emitter}
 * @api public
 */

Emitter.prototype.off =
Emitter.prototype.removeListener =
Emitter.prototype.removeAllListeners =
Emitter.prototype.removeEventListener = function(event, fn){
  this._callbacks = this._callbacks || {};

  // all
  if (0 == arguments.length) {
    this._callbacks = {};
    return this;
  }

  // specific event
  var callbacks = this._callbacks[event];
  if (!callbacks) return this;

  // remove all handlers
  if (1 == arguments.length) {
    delete this._callbacks[event];
    return this;
  }

  // remove specific handler
  var cb;
  for (var i = 0; i < callbacks.length; i++) {
    cb = callbacks[i];
    if (cb === fn || cb.fn === fn) {
      callbacks.splice(i, 1);
      break;
    }
  }
  return this;
};

/**
 * Emit `event` with the given args.
 *
 * @param {String} event
 * @param {Mixed} ...
 * @return {Emitter}
 */

Emitter.prototype.emit = function(event){
  this._callbacks = this._callbacks || {};
  var args = [].slice.call(arguments, 1)
    , callbacks = this._callbacks[event];

  if (callbacks) {
    callbacks = callbacks.slice(0);
    for (var i = 0, len = callbacks.length; i < len; ++i) {
      callbacks[i].apply(this, args);
    }
  }

  return this;
};

/**
 * Return array of callbacks for `event`.
 *
 * @param {String} event
 * @return {Array}
 * @api public
 */

Emitter.prototype.listeners = function(event){
  this._callbacks = this._callbacks || {};
  return this._callbacks[event] || [];
};

/**
 * Check if this emitter has `event` handlers.
 *
 * @param {String} event
 * @return {Boolean}
 * @api public
 */

Emitter.prototype.hasListeners = function(event){
  return !! this.listeners(event).length;
};

});

require.register("dropzone", function (exports, module) {


/**
 * Exposing dropzone
 */
module.exports = require("dropzone/lib/dropzone.js");

});

require.register("dropzone/lib/dropzone.js", function (exports, module) {

/*
 *
 * More info at [www.dropzonejs.com](http://www.dropzonejs.com)
 *
 * Copyright (c) 2012, Matias Meno
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 */

(function() {
  var Dropzone, Em, camelize, contentLoaded, detectVerticalSquash, drawImageIOSFix, noop, without,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
    __slice = [].slice;

  Em = typeof Emitter !== "undefined" && Emitter !== null ? Emitter : require("component~emitter@1.1.2");

  noop = function() {};

  Dropzone = (function(_super) {
    var extend;

    __extends(Dropzone, _super);


    /*
    This is a list of all available events you can register on a dropzone object.

    You can register an event handler like this:

        dropzone.on("dragEnter", function() { });
     */

    Dropzone.prototype.events = ["drop", "dragstart", "dragend", "dragenter", "dragover", "dragleave", "addedfile", "removedfile", "thumbnail", "error", "errormultiple", "processing", "processingmultiple", "uploadprogress", "totaluploadprogress", "sending", "sendingmultiple", "success", "successmultiple", "canceled", "canceledmultiple", "complete", "completemultiple", "reset", "maxfilesexceeded", "maxfilesreached"];

    Dropzone.prototype.defaultOptions = {
      url: null,
      method: "post",
      withCredentials: false,
      parallelUploads: 2,
      uploadMultiple: false,
      maxFilesize: 256,
      paramName: "file",
      createImageThumbnails: true,
      maxThumbnailFilesize: 10,
      thumbnailWidth: 100,
      thumbnailHeight: 100,
      maxFiles: null,
      params: {},
      clickable: true,
      ignoreHiddenFiles: true,
      acceptedFiles: null,
      acceptedMimeTypes: null,
      autoProcessQueue: true,
      autoQueue: true,
      addRemoveLinks: false,
      previewsContainer: null,
      dictDefaultMessage: "Drop files here to upload",
      dictFallbackMessage: "Your browser does not support drag'n'drop file uploads.",
      dictFallbackText: "Please use the fallback form below to upload your files like in the olden days.",
      dictFileTooBig: "File is too big ({{filesize}}MiB). Max filesize: {{maxFilesize}}MiB.",
      dictInvalidFileType: "You can't upload files of this type.",
      dictResponseError: "Server responded with {{statusCode}} code.",
      dictCancelUpload: "Cancel upload",
      dictCancelUploadConfirmation: "Are you sure you want to cancel this upload?",
      dictRemoveFile: "Remove file",
      dictRemoveFileConfirmation: null,
      dictMaxFilesExceeded: "You can not upload any more files.",
      accept: function(file, done) {
        return done();
      },
      init: function() {
        return noop;
      },
      forceFallback: false,
      fallback: function() {
        var child, messageElement, span, _i, _len, _ref;
        this.element.className = "" + this.element.className + " dz-browser-not-supported";
        _ref = this.element.getElementsByTagName("div");
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          child = _ref[_i];
          if (/(^| )dz-message($| )/.test(child.className)) {
            messageElement = child;
            child.className = "dz-message";
            continue;
          }
        }
        if (!messageElement) {
          messageElement = Dropzone.createElement("<div class=\"dz-message\"><span></span></div>");
          this.element.appendChild(messageElement);
        }
        span = messageElement.getElementsByTagName("span")[0];
        if (span) {
          span.textContent = this.options.dictFallbackMessage;
        }
        return this.element.appendChild(this.getFallbackForm());
      },
      resize: function(file) {
        var info, srcRatio, trgRatio;
        info = {
          srcX: 0,
          srcY: 0,
          srcWidth: file.width,
          srcHeight: file.height
        };
        srcRatio = file.width / file.height;
        info.optWidth = this.options.thumbnailWidth;
        info.optHeight = this.options.thumbnailHeight;
        if ((info.optWidth == null) && (info.optHeight == null)) {
          info.optWidth = info.srcWidth;
          info.optHeight = info.srcHeight;
        } else if (info.optWidth == null) {
          info.optWidth = srcRatio * info.optHeight;
        } else if (info.optHeight == null) {
          info.optHeight = (1 / srcRatio) * info.optWidth;
        }
        trgRatio = info.optWidth / info.optHeight;
        if (file.height < info.optHeight || file.width < info.optWidth) {
          info.trgHeight = info.srcHeight;
          info.trgWidth = info.srcWidth;
        } else {
          if (srcRatio > trgRatio) {
            info.srcHeight = file.height;
            info.srcWidth = info.srcHeight * trgRatio;
          } else {
            info.srcWidth = file.width;
            info.srcHeight = info.srcWidth / trgRatio;
          }
        }
        info.srcX = (file.width - info.srcWidth) / 2;
        info.srcY = (file.height - info.srcHeight) / 2;
        return info;
      },

      /*
      Those functions register themselves to the events on init and handle all
      the user interface specific stuff. Overwriting them won't break the upload
      but can break the way it's displayed.
      You can overwrite them if you don't like the default behavior. If you just
      want to add an additional event handler, register it on the dropzone object
      and don't overwrite those options.
       */
      drop: function(e) {
        return this.element.classList.remove("dz-drag-hover");
      },
      dragstart: noop,
      dragend: function(e) {
        return this.element.classList.remove("dz-drag-hover");
      },
      dragenter: function(e) {
        return this.element.classList.add("dz-drag-hover");
      },
      dragover: function(e) {
        return this.element.classList.add("dz-drag-hover");
      },
      dragleave: function(e) {
        return this.element.classList.remove("dz-drag-hover");
      },
      paste: noop,
      reset: function() {
        return this.element.classList.remove("dz-started");
      },
      addedfile: function(file) {
        var node, removeFileEvent, removeLink, _i, _j, _k, _len, _len1, _len2, _ref, _ref1, _ref2, _results;
        if (this.element === this.previewsContainer) {
          this.element.classList.add("dz-started");
        }
        if (this.previewsContainer) {
          file.previewElement = Dropzone.createElement(this.options.previewTemplate.trim());
          file.previewTemplate = file.previewElement;
          this.previewsContainer.appendChild(file.previewElement);
          _ref = file.previewElement.querySelectorAll("[data-dz-name]");
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            node = _ref[_i];
            node.textContent = file.name;
          }
          _ref1 = file.previewElement.querySelectorAll("[data-dz-size]");
          for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
            node = _ref1[_j];
            node.innerHTML = this.filesize(file.size);
          }
          if (this.options.addRemoveLinks) {
            file._removeLink = Dropzone.createElement("<a class=\"dz-remove\" href=\"javascript:undefined;\" data-dz-remove>" + this.options.dictRemoveFile + "</a>");
            file.previewElement.appendChild(file._removeLink);
          }
          removeFileEvent = (function(_this) {
            return function(e) {
              e.preventDefault();
              e.stopPropagation();
              if (file.status === Dropzone.UPLOADING) {
                return Dropzone.confirm(_this.options.dictCancelUploadConfirmation, function() {
                  return _this.removeFile(file);
                });
              } else {
                if (_this.options.dictRemoveFileConfirmation) {
                  return Dropzone.confirm(_this.options.dictRemoveFileConfirmation, function() {
                    return _this.removeFile(file);
                  });
                } else {
                  return _this.removeFile(file);
                }
              }
            };
          })(this);
          _ref2 = file.previewElement.querySelectorAll("[data-dz-remove]");
          _results = [];
          for (_k = 0, _len2 = _ref2.length; _k < _len2; _k++) {
            removeLink = _ref2[_k];
            _results.push(removeLink.addEventListener("click", removeFileEvent));
          }
          return _results;
        }
      },
      removedfile: function(file) {
        var _ref;
        if (file.previewElement) {
          if ((_ref = file.previewElement) != null) {
            _ref.parentNode.removeChild(file.previewElement);
          }
        }
        return this._updateMaxFilesReachedClass();
      },
      thumbnail: function(file, dataUrl) {
        var thumbnailElement, _i, _len, _ref, _results;
        if (file.previewElement) {
          file.previewElement.classList.remove("dz-file-preview");
          file.previewElement.classList.add("dz-image-preview");
          _ref = file.previewElement.querySelectorAll("[data-dz-thumbnail]");
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            thumbnailElement = _ref[_i];
            thumbnailElement.alt = file.name;
            _results.push(thumbnailElement.src = dataUrl);
          }
          return _results;
        }
      },
      error: function(file, message) {
        var node, _i, _len, _ref, _results;
        if (file.previewElement) {
          file.previewElement.classList.add("dz-error");
          if (typeof message !== "String" && message.error) {
            message = message.error;
          }
          _ref = file.previewElement.querySelectorAll("[data-dz-errormessage]");
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            node = _ref[_i];
            _results.push(node.textContent = message);
          }
          return _results;
        }
      },
      errormultiple: noop,
      processing: function(file) {
        if (file.previewElement) {
          file.previewElement.classList.add("dz-processing");
          if (file._removeLink) {
            return file._removeLink.textContent = this.options.dictCancelUpload;
          }
        }
      },
      processingmultiple: noop,
      uploadprogress: function(file, progress, bytesSent) {
        var node, _i, _len, _ref, _results;
        if (file.previewElement) {
          _ref = file.previewElement.querySelectorAll("[data-dz-uploadprogress]");
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            node = _ref[_i];
            _results.push(node.style.width = "" + progress + "%");
          }
          return _results;
        }
      },
      totaluploadprogress: noop,
      sending: noop,
      sendingmultiple: noop,
      success: function(file) {
        if (file.previewElement) {
          return file.previewElement.classList.add("dz-success");
        }
      },
      successmultiple: noop,
      canceled: function(file) {
        return this.emit("error", file, "Upload canceled.");
      },
      canceledmultiple: noop,
      complete: function(file) {
        if (file._removeLink) {
          return file._removeLink.textContent = this.options.dictRemoveFile;
        }
      },
      completemultiple: noop,
      maxfilesexceeded: noop,
      maxfilesreached: noop,
      previewTemplate: "<div class=\"dz-preview dz-file-preview\">\n  <div class=\"dz-details\">\n    <div class=\"dz-filename\"><span data-dz-name></span></div>\n    <div class=\"dz-size\" data-dz-size></div>\n    <img data-dz-thumbnail />\n  </div>\n  <div class=\"dz-progress\"><span class=\"dz-upload\" data-dz-uploadprogress></span></div>\n  <div class=\"dz-success-mark\"><span>✔</span></div>\n  <div class=\"dz-error-mark\"><span>✘</span></div>\n  <div class=\"dz-error-message\"><span data-dz-errormessage></span></div>\n</div>"
    };

    extend = function() {
      var key, object, objects, target, val, _i, _len;
      target = arguments[0], objects = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
      for (_i = 0, _len = objects.length; _i < _len; _i++) {
        object = objects[_i];
        for (key in object) {
          val = object[key];
          target[key] = val;
        }
      }
      return target;
    };

    function Dropzone(element, options) {
      var elementOptions, fallback, _ref;
      this.element = element;
      this.version = Dropzone.version;
      this.defaultOptions.previewTemplate = this.defaultOptions.previewTemplate.replace(/\n*/g, "");
      this.clickableElements = [];
      this.listeners = [];
      this.files = [];
      if (typeof this.element === "string") {
        this.element = document.querySelector(this.element);
      }
      if (!(this.element && (this.element.nodeType != null))) {
        throw new Error("Invalid dropzone element.");
      }
      if (this.element.dropzone) {
        throw new Error("Dropzone already attached.");
      }
      Dropzone.instances.push(this);
      this.element.dropzone = this;
      elementOptions = (_ref = Dropzone.optionsForElement(this.element)) != null ? _ref : {};
      this.options = extend({}, this.defaultOptions, elementOptions, options != null ? options : {});
      if (this.options.forceFallback || !Dropzone.isBrowserSupported()) {
        return this.options.fallback.call(this);
      }
      if (this.options.url == null) {
        this.options.url = this.element.getAttribute("action");
      }
      if (!this.options.url) {
        throw new Error("No URL provided.");
      }
      if (this.options.acceptedFiles && this.options.acceptedMimeTypes) {
        throw new Error("You can't provide both 'acceptedFiles' and 'acceptedMimeTypes'. 'acceptedMimeTypes' is deprecated.");
      }
      if (this.options.acceptedMimeTypes) {
        this.options.acceptedFiles = this.options.acceptedMimeTypes;
        delete this.options.acceptedMimeTypes;
      }
      this.options.method = this.options.method.toUpperCase();
      if ((fallback = this.getExistingFallback()) && fallback.parentNode) {
        fallback.parentNode.removeChild(fallback);
      }
      if (this.options.previewsContainer !== false) {
        if (this.options.previewsContainer) {
          this.previewsContainer = Dropzone.getElement(this.options.previewsContainer, "previewsContainer");
        } else {
          this.previewsContainer = this.element;
        }
      }
      if (this.options.clickable) {
        if (this.options.clickable === true) {
          this.clickableElements = [this.element];
        } else {
          this.clickableElements = Dropzone.getElements(this.options.clickable, "clickable");
        }
      }
      this.init();
    }

    Dropzone.prototype.getAcceptedFiles = function() {
      var file, _i, _len, _ref, _results;
      _ref = this.files;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        file = _ref[_i];
        if (file.accepted) {
          _results.push(file);
        }
      }
      return _results;
    };

    Dropzone.prototype.getRejectedFiles = function() {
      var file, _i, _len, _ref, _results;
      _ref = this.files;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        file = _ref[_i];
        if (!file.accepted) {
          _results.push(file);
        }
      }
      return _results;
    };

    Dropzone.prototype.getFilesWithStatus = function(status) {
      var file, _i, _len, _ref, _results;
      _ref = this.files;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        file = _ref[_i];
        if (file.status === status) {
          _results.push(file);
        }
      }
      return _results;
    };

    Dropzone.prototype.getQueuedFiles = function() {
      return this.getFilesWithStatus(Dropzone.QUEUED);
    };

    Dropzone.prototype.getUploadingFiles = function() {
      return this.getFilesWithStatus(Dropzone.UPLOADING);
    };

    Dropzone.prototype.getActiveFiles = function() {
      var file, _i, _len, _ref, _results;
      _ref = this.files;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        file = _ref[_i];
        if (file.status === Dropzone.UPLOADING || file.status === Dropzone.QUEUED) {
          _results.push(file);
        }
      }
      return _results;
    };

    Dropzone.prototype.init = function() {
      var eventName, noPropagation, setupHiddenFileInput, _i, _len, _ref, _ref1;
      if (this.element.tagName === "form") {
        this.element.setAttribute("enctype", "multipart/form-data");
      }
      if (this.element.classList.contains("dropzone") && !this.element.querySelector(".dz-message")) {
        this.element.appendChild(Dropzone.createElement("<div class=\"dz-default dz-message\"><span>" + this.options.dictDefaultMessage + "</span></div>"));
      }
      if (this.clickableElements.length) {
        setupHiddenFileInput = (function(_this) {
          return function() {
            if (_this.hiddenFileInput) {
              document.body.removeChild(_this.hiddenFileInput);
            }
            _this.hiddenFileInput = document.createElement("input");
            _this.hiddenFileInput.setAttribute("type", "file");
            if ((_this.options.maxFiles == null) || _this.options.maxFiles > 1) {
              _this.hiddenFileInput.setAttribute("multiple", "multiple");
            }
            _this.hiddenFileInput.className = "dz-hidden-input";
            if (_this.options.acceptedFiles != null) {
              _this.hiddenFileInput.setAttribute("accept", _this.options.acceptedFiles);
            }
            _this.hiddenFileInput.style.visibility = "hidden";
            _this.hiddenFileInput.style.position = "absolute";
            _this.hiddenFileInput.style.top = "0";
            _this.hiddenFileInput.style.left = "0";
            _this.hiddenFileInput.style.height = "0";
            _this.hiddenFileInput.style.width = "0";
            document.body.appendChild(_this.hiddenFileInput);
            return _this.hiddenFileInput.addEventListener("change", function() {
              var file, files, _i, _len;
              files = _this.hiddenFileInput.files;
              if (files.length) {
                for (_i = 0, _len = files.length; _i < _len; _i++) {
                  file = files[_i];
                  _this.addFile(file);
                }
              }
              return setupHiddenFileInput();
            });
          };
        })(this);
        setupHiddenFileInput();
      }
      this.URL = (_ref = window.URL) != null ? _ref : window.webkitURL;
      _ref1 = this.events;
      for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
        eventName = _ref1[_i];
        this.on(eventName, this.options[eventName]);
      }
      this.on("uploadprogress", (function(_this) {
        return function() {
          return _this.updateTotalUploadProgress();
        };
      })(this));
      this.on("removedfile", (function(_this) {
        return function() {
          return _this.updateTotalUploadProgress();
        };
      })(this));
      this.on("canceled", (function(_this) {
        return function(file) {
          return _this.emit("complete", file);
        };
      })(this));
      this.on("complete", (function(_this) {
        return function(file) {
          if (_this.getUploadingFiles().length === 0 && _this.getQueuedFiles().length === 0) {
            return setTimeout((function() {
              return _this.emit("queuecomplete");
            }), 0);
          }
        };
      })(this));
      noPropagation = function(e) {
        e.stopPropagation();
        if (e.preventDefault) {
          return e.preventDefault();
        } else {
          return e.returnValue = false;
        }
      };
      this.listeners = [
        {
          element: this.element,
          events: {
            "dragstart": (function(_this) {
              return function(e) {
                return _this.emit("dragstart", e);
              };
            })(this),
            "dragenter": (function(_this) {
              return function(e) {
                noPropagation(e);
                return _this.emit("dragenter", e);
              };
            })(this),
            "dragover": (function(_this) {
              return function(e) {
                var efct;
                try {
                  efct = e.dataTransfer.effectAllowed;
                } catch (_error) {}
                e.dataTransfer.dropEffect = 'move' === efct || 'linkMove' === efct ? 'move' : 'copy';
                noPropagation(e);
                return _this.emit("dragover", e);
              };
            })(this),
            "dragleave": (function(_this) {
              return function(e) {
                return _this.emit("dragleave", e);
              };
            })(this),
            "drop": (function(_this) {
              return function(e) {
                noPropagation(e);
                return _this.drop(e);
              };
            })(this),
            "dragend": (function(_this) {
              return function(e) {
                return _this.emit("dragend", e);
              };
            })(this)
          }
        }
      ];
      this.clickableElements.forEach((function(_this) {
        return function(clickableElement) {
          return _this.listeners.push({
            element: clickableElement,
            events: {
              "click": function(evt) {
                if ((clickableElement !== _this.element) || (evt.target === _this.element || Dropzone.elementInside(evt.target, _this.element.querySelector(".dz-message")))) {
                  return _this.hiddenFileInput.click();
                }
              }
            }
          });
        };
      })(this));
      this.enable();
      return this.options.init.call(this);
    };

    Dropzone.prototype.destroy = function() {
      var _ref;
      this.disable();
      this.removeAllFiles(true);
      if ((_ref = this.hiddenFileInput) != null ? _ref.parentNode : void 0) {
        this.hiddenFileInput.parentNode.removeChild(this.hiddenFileInput);
        this.hiddenFileInput = null;
      }
      delete this.element.dropzone;
      return Dropzone.instances.splice(Dropzone.instances.indexOf(this), 1);
    };

    Dropzone.prototype.updateTotalUploadProgress = function() {
      var activeFiles, file, totalBytes, totalBytesSent, totalUploadProgress, _i, _len, _ref;
      totalBytesSent = 0;
      totalBytes = 0;
      activeFiles = this.getActiveFiles();
      if (activeFiles.length) {
        _ref = this.getActiveFiles();
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          file = _ref[_i];
          totalBytesSent += file.upload.bytesSent;
          totalBytes += file.upload.total;
        }
        totalUploadProgress = 100 * totalBytesSent / totalBytes;
      } else {
        totalUploadProgress = 100;
      }
      return this.emit("totaluploadprogress", totalUploadProgress, totalBytes, totalBytesSent);
    };

    Dropzone.prototype._getParamName = function(n) {
      if (typeof this.options.paramName === "function") {
        return this.options.paramName(n);
      } else {
        return "" + this.options.paramName + (this.options.uploadMultiple ? "[" + n + "]" : "");
      }
    };

    Dropzone.prototype.getFallbackForm = function() {
      var existingFallback, fields, fieldsString, form;
      if (existingFallback = this.getExistingFallback()) {
        return existingFallback;
      }
      fieldsString = "<div class=\"dz-fallback\">";
      if (this.options.dictFallbackText) {
        fieldsString += "<p>" + this.options.dictFallbackText + "</p>";
      }
      fieldsString += "<input type=\"file\" name=\"" + (this._getParamName(0)) + "\" " + (this.options.uploadMultiple ? 'multiple="multiple"' : void 0) + " /><input type=\"submit\" value=\"Upload!\"></div>";
      fields = Dropzone.createElement(fieldsString);
      if (this.element.tagName !== "FORM") {
        form = Dropzone.createElement("<form action=\"" + this.options.url + "\" enctype=\"multipart/form-data\" method=\"" + this.options.method + "\"></form>");
        form.appendChild(fields);
      } else {
        this.element.setAttribute("enctype", "multipart/form-data");
        this.element.setAttribute("method", this.options.method);
      }
      return form != null ? form : fields;
    };

    Dropzone.prototype.getExistingFallback = function() {
      var fallback, getFallback, tagName, _i, _len, _ref;
      getFallback = function(elements) {
        var el, _i, _len;
        for (_i = 0, _len = elements.length; _i < _len; _i++) {
          el = elements[_i];
          if (/(^| )fallback($| )/.test(el.className)) {
            return el;
          }
        }
      };
      _ref = ["div", "form"];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        tagName = _ref[_i];
        if (fallback = getFallback(this.element.getElementsByTagName(tagName))) {
          return fallback;
        }
      }
    };

    Dropzone.prototype.setupEventListeners = function() {
      var elementListeners, event, listener, _i, _len, _ref, _results;
      _ref = this.listeners;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        elementListeners = _ref[_i];
        _results.push((function() {
          var _ref1, _results1;
          _ref1 = elementListeners.events;
          _results1 = [];
          for (event in _ref1) {
            listener = _ref1[event];
            _results1.push(elementListeners.element.addEventListener(event, listener, false));
          }
          return _results1;
        })());
      }
      return _results;
    };

    Dropzone.prototype.removeEventListeners = function() {
      var elementListeners, event, listener, _i, _len, _ref, _results;
      _ref = this.listeners;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        elementListeners = _ref[_i];
        _results.push((function() {
          var _ref1, _results1;
          _ref1 = elementListeners.events;
          _results1 = [];
          for (event in _ref1) {
            listener = _ref1[event];
            _results1.push(elementListeners.element.removeEventListener(event, listener, false));
          }
          return _results1;
        })());
      }
      return _results;
    };

    Dropzone.prototype.disable = function() {
      var file, _i, _len, _ref, _results;
      this.clickableElements.forEach(function(element) {
        return element.classList.remove("dz-clickable");
      });
      this.removeEventListeners();
      _ref = this.files;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        file = _ref[_i];
        _results.push(this.cancelUpload(file));
      }
      return _results;
    };

    Dropzone.prototype.enable = function() {
      this.clickableElements.forEach(function(element) {
        return element.classList.add("dz-clickable");
      });
      return this.setupEventListeners();
    };

    Dropzone.prototype.filesize = function(size) {
      var string;
      if (size >= 1024 * 1024 * 1024 * 1024 / 10) {
        size = size / (1024 * 1024 * 1024 * 1024 / 10);
        string = "TiB";
      } else if (size >= 1024 * 1024 * 1024 / 10) {
        size = size / (1024 * 1024 * 1024 / 10);
        string = "GiB";
      } else if (size >= 1024 * 1024 / 10) {
        size = size / (1024 * 1024 / 10);
        string = "MiB";
      } else if (size >= 1024 / 10) {
        size = size / (1024 / 10);
        string = "KiB";
      } else {
        size = size * 10;
        string = "b";
      }
      return "<strong>" + (Math.round(size) / 10) + "</strong> " + string;
    };

    Dropzone.prototype._updateMaxFilesReachedClass = function() {
      if ((this.options.maxFiles != null) && this.getAcceptedFiles().length >= this.options.maxFiles) {
        if (this.getAcceptedFiles().length === this.options.maxFiles) {
          this.emit('maxfilesreached', this.files);
        }
        return this.element.classList.add("dz-max-files-reached");
      } else {
        return this.element.classList.remove("dz-max-files-reached");
      }
    };

    Dropzone.prototype.drop = function(e) {
      var files, items;
      if (!e.dataTransfer) {
        return;
      }
      this.emit("drop", e);
      files = e.dataTransfer.files;
      if (files.length) {
        items = e.dataTransfer.items;
        if (items && items.length && (items[0].webkitGetAsEntry != null)) {
          this._addFilesFromItems(items);
        } else {
          this.handleFiles(files);
        }
      }
    };

    Dropzone.prototype.paste = function(e) {
      var items, _ref;
      if ((e != null ? (_ref = e.clipboardData) != null ? _ref.items : void 0 : void 0) == null) {
        return;
      }
      this.emit("paste", e);
      items = e.clipboardData.items;
      if (items.length) {
        return this._addFilesFromItems(items);
      }
    };

    Dropzone.prototype.handleFiles = function(files) {
      var file, _i, _len, _results;
      _results = [];
      for (_i = 0, _len = files.length; _i < _len; _i++) {
        file = files[_i];
        _results.push(this.addFile(file));
      }
      return _results;
    };

    Dropzone.prototype._addFilesFromItems = function(items) {
      var entry, item, _i, _len, _results;
      _results = [];
      for (_i = 0, _len = items.length; _i < _len; _i++) {
        item = items[_i];
        if ((item.webkitGetAsEntry != null) && (entry = item.webkitGetAsEntry())) {
          if (entry.isFile) {
            _results.push(this.addFile(item.getAsFile()));
          } else if (entry.isDirectory) {
            _results.push(this._addFilesFromDirectory(entry, entry.name));
          } else {
            _results.push(void 0);
          }
        } else if (item.getAsFile != null) {
          if ((item.kind == null) || item.kind === "file") {
            _results.push(this.addFile(item.getAsFile()));
          } else {
            _results.push(void 0);
          }
        } else {
          _results.push(void 0);
        }
      }
      return _results;
    };

    Dropzone.prototype._addFilesFromDirectory = function(directory, path) {
      var dirReader, entriesReader;
      dirReader = directory.createReader();
      entriesReader = (function(_this) {
        return function(entries) {
          var entry, _i, _len;
          for (_i = 0, _len = entries.length; _i < _len; _i++) {
            entry = entries[_i];
            if (entry.isFile) {
              entry.file(function(file) {
                if (_this.options.ignoreHiddenFiles && file.name.substring(0, 1) === '.') {
                  return;
                }
                file.fullPath = "" + path + "/" + file.name;
                return _this.addFile(file);
              });
            } else if (entry.isDirectory) {
              _this._addFilesFromDirectory(entry, "" + path + "/" + entry.name);
            }
          }
        };
      })(this);
      return dirReader.readEntries(entriesReader, function(error) {
        return typeof console !== "undefined" && console !== null ? typeof console.log === "function" ? console.log(error) : void 0 : void 0;
      });
    };

    Dropzone.prototype.accept = function(file, done) {
      if (file.size > this.options.maxFilesize * 1024 * 1024) {
        return done(this.options.dictFileTooBig.replace("{{filesize}}", Math.round(file.size / 1024 / 10.24) / 100).replace("{{maxFilesize}}", this.options.maxFilesize));
      } else if (!Dropzone.isValidFile(file, this.options.acceptedFiles)) {
        return done(this.options.dictInvalidFileType);
      } else if ((this.options.maxFiles != null) && this.getAcceptedFiles().length >= this.options.maxFiles) {
        done(this.options.dictMaxFilesExceeded.replace("{{maxFiles}}", this.options.maxFiles));
        return this.emit("maxfilesexceeded", file);
      } else {
        return this.options.accept.call(this, file, done);
      }
    };

    Dropzone.prototype.addFile = function(file) {
      file.upload = {
        progress: 0,
        total: file.size,
        bytesSent: 0
      };
      this.files.push(file);
      file.status = Dropzone.ADDED;
      this.emit("addedfile", file);
      this._enqueueThumbnail(file);
      return this.accept(file, (function(_this) {
        return function(error) {
          if (error) {
            file.accepted = false;
            _this._errorProcessing([file], error);
          } else {
            file.accepted = true;
            if (_this.options.autoQueue) {
              _this.enqueueFile(file);
            }
          }
          return _this._updateMaxFilesReachedClass();
        };
      })(this));
    };

    Dropzone.prototype.enqueueFiles = function(files) {
      var file, _i, _len;
      for (_i = 0, _len = files.length; _i < _len; _i++) {
        file = files[_i];
        this.enqueueFile(file);
      }
      return null;
    };

    Dropzone.prototype.enqueueFile = function(file) {
      if (file.status === Dropzone.ADDED && file.accepted === true) {
        file.status = Dropzone.QUEUED;
        if (this.options.autoProcessQueue) {
          return setTimeout(((function(_this) {
            return function() {
              return _this.processQueue();
            };
          })(this)), 0);
        }
      } else {
        throw new Error("This file can't be queued because it has already been processed or was rejected.");
      }
    };

    Dropzone.prototype._thumbnailQueue = [];

    Dropzone.prototype._processingThumbnail = false;

    Dropzone.prototype._enqueueThumbnail = function(file) {
      if (this.options.createImageThumbnails && file.type.match(/image.*/) && file.size <= this.options.maxThumbnailFilesize * 1024 * 1024) {
        this._thumbnailQueue.push(file);
        return setTimeout(((function(_this) {
          return function() {
            return _this._processThumbnailQueue();
          };
        })(this)), 0);
      }
    };

    Dropzone.prototype._processThumbnailQueue = function() {
      if (this._processingThumbnail || this._thumbnailQueue.length === 0) {
        return;
      }
      this._processingThumbnail = true;
      return this.createThumbnail(this._thumbnailQueue.shift(), (function(_this) {
        return function() {
          _this._processingThumbnail = false;
          return _this._processThumbnailQueue();
        };
      })(this));
    };

    Dropzone.prototype.removeFile = function(file) {
      if (file.status === Dropzone.UPLOADING) {
        this.cancelUpload(file);
      }
      this.files = without(this.files, file);
      this.emit("removedfile", file);
      if (this.files.length === 0) {
        return this.emit("reset");
      }
    };

    Dropzone.prototype.removeAllFiles = function(cancelIfNecessary) {
      var file, _i, _len, _ref;
      if (cancelIfNecessary == null) {
        cancelIfNecessary = false;
      }
      _ref = this.files.slice();
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        file = _ref[_i];
        if (file.status !== Dropzone.UPLOADING || cancelIfNecessary) {
          this.removeFile(file);
        }
      }
      return null;
    };

    Dropzone.prototype.createThumbnail = function(file, callback) {
      var fileReader;
      fileReader = new FileReader;
      fileReader.onload = (function(_this) {
        return function() {
          var img;
          img = document.createElement("img");
          img.onload = function() {
            var canvas, ctx, resizeInfo, thumbnail, _ref, _ref1, _ref2, _ref3;
            file.width = img.width;
            file.height = img.height;
            resizeInfo = _this.options.resize.call(_this, file);
            if (resizeInfo.trgWidth == null) {
              resizeInfo.trgWidth = resizeInfo.optWidth;
            }
            if (resizeInfo.trgHeight == null) {
              resizeInfo.trgHeight = resizeInfo.optHeight;
            }
            canvas = document.createElement("canvas");
            ctx = canvas.getContext("2d");
            canvas.width = resizeInfo.trgWidth;
            canvas.height = resizeInfo.trgHeight;
            drawImageIOSFix(ctx, img, (_ref = resizeInfo.srcX) != null ? _ref : 0, (_ref1 = resizeInfo.srcY) != null ? _ref1 : 0, resizeInfo.srcWidth, resizeInfo.srcHeight, (_ref2 = resizeInfo.trgX) != null ? _ref2 : 0, (_ref3 = resizeInfo.trgY) != null ? _ref3 : 0, resizeInfo.trgWidth, resizeInfo.trgHeight);
            thumbnail = canvas.toDataURL("image/png");
            _this.emit("thumbnail", file, thumbnail);
            if (callback != null) {
              return callback();
            }
          };
          return img.src = fileReader.result;
        };
      })(this);
      return fileReader.readAsDataURL(file);
    };

    Dropzone.prototype.processQueue = function() {
      var i, parallelUploads, processingLength, queuedFiles;
      parallelUploads = this.options.parallelUploads;
      processingLength = this.getUploadingFiles().length;
      i = processingLength;
      if (processingLength >= parallelUploads) {
        return;
      }
      queuedFiles = this.getQueuedFiles();
      if (!(queuedFiles.length > 0)) {
        return;
      }
      if (this.options.uploadMultiple) {
        return this.processFiles(queuedFiles.slice(0, parallelUploads - processingLength));
      } else {
        while (i < parallelUploads) {
          if (!queuedFiles.length) {
            return;
          }
          this.processFile(queuedFiles.shift());
          i++;
        }
      }
    };

    Dropzone.prototype.processFile = function(file) {
      return this.processFiles([file]);
    };

    Dropzone.prototype.processFiles = function(files) {
      var file, _i, _len;
      for (_i = 0, _len = files.length; _i < _len; _i++) {
        file = files[_i];
        file.processing = true;
        file.status = Dropzone.UPLOADING;
        this.emit("processing", file);
      }
      if (this.options.uploadMultiple) {
        this.emit("processingmultiple", files);
      }
      return this.uploadFiles(files);
    };

    Dropzone.prototype._getFilesWithXhr = function(xhr) {
      var file, files;
      return files = (function() {
        var _i, _len, _ref, _results;
        _ref = this.files;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          file = _ref[_i];
          if (file.xhr === xhr) {
            _results.push(file);
          }
        }
        return _results;
      }).call(this);
    };

    Dropzone.prototype.cancelUpload = function(file) {
      var groupedFile, groupedFiles, _i, _j, _len, _len1, _ref;
      if (file.status === Dropzone.UPLOADING) {
        groupedFiles = this._getFilesWithXhr(file.xhr);
        for (_i = 0, _len = groupedFiles.length; _i < _len; _i++) {
          groupedFile = groupedFiles[_i];
          groupedFile.status = Dropzone.CANCELED;
        }
        file.xhr.abort();
        for (_j = 0, _len1 = groupedFiles.length; _j < _len1; _j++) {
          groupedFile = groupedFiles[_j];
          this.emit("canceled", groupedFile);
        }
        if (this.options.uploadMultiple) {
          this.emit("canceledmultiple", groupedFiles);
        }
      } else if ((_ref = file.status) === Dropzone.ADDED || _ref === Dropzone.QUEUED) {
        file.status = Dropzone.CANCELED;
        this.emit("canceled", file);
        if (this.options.uploadMultiple) {
          this.emit("canceledmultiple", [file]);
        }
      }
      if (this.options.autoProcessQueue) {
        return this.processQueue();
      }
    };

    Dropzone.prototype.uploadFile = function(file) {
      return this.uploadFiles([file]);
    };

    Dropzone.prototype.uploadFiles = function(files) {
      var file, formData, handleError, headerName, headerValue, headers, i, input, inputName, inputType, key, option, progressObj, response, updateProgress, value, xhr, _i, _j, _k, _l, _len, _len1, _len2, _len3, _m, _ref, _ref1, _ref2, _ref3, _ref4, _ref5;
      xhr = new XMLHttpRequest();
      for (_i = 0, _len = files.length; _i < _len; _i++) {
        file = files[_i];
        file.xhr = xhr;
      }
      xhr.open(this.options.method, this.options.url, true);
      xhr.withCredentials = !!this.options.withCredentials;
      response = null;
      handleError = (function(_this) {
        return function() {
          var _j, _len1, _results;
          _results = [];
          for (_j = 0, _len1 = files.length; _j < _len1; _j++) {
            file = files[_j];
            _results.push(_this._errorProcessing(files, response || _this.options.dictResponseError.replace("{{statusCode}}", xhr.status), xhr));
          }
          return _results;
        };
      })(this);
      updateProgress = (function(_this) {
        return function(e) {
          var allFilesFinished, progress, _j, _k, _l, _len1, _len2, _len3, _results;
          if (e != null) {
            progress = 100 * e.loaded / e.total;
            for (_j = 0, _len1 = files.length; _j < _len1; _j++) {
              file = files[_j];
              file.upload = {
                progress: progress,
                total: e.total,
                bytesSent: e.loaded
              };
            }
          } else {
            allFilesFinished = true;
            progress = 100;
            for (_k = 0, _len2 = files.length; _k < _len2; _k++) {
              file = files[_k];
              if (!(file.upload.progress === 100 && file.upload.bytesSent === file.upload.total)) {
                allFilesFinished = false;
              }
              file.upload.progress = progress;
              file.upload.bytesSent = file.upload.total;
            }
            if (allFilesFinished) {
              return;
            }
          }
          _results = [];
          for (_l = 0, _len3 = files.length; _l < _len3; _l++) {
            file = files[_l];
            _results.push(_this.emit("uploadprogress", file, progress, file.upload.bytesSent));
          }
          return _results;
        };
      })(this);
      xhr.onload = (function(_this) {
        return function(e) {
          var _ref;
          if (files[0].status === Dropzone.CANCELED) {
            return;
          }
          if (xhr.readyState !== 4) {
            return;
          }
          response = xhr.responseText;
          if (xhr.getResponseHeader("content-type") && ~xhr.getResponseHeader("content-type").indexOf("application/json")) {
            try {
              response = JSON.parse(response);
            } catch (_error) {
              e = _error;
              response = "Invalid JSON response from server.";
            }
          }
          updateProgress();
          if (!((200 <= (_ref = xhr.status) && _ref < 300))) {
            return handleError();
          } else {
            return _this._finished(files, response, e);
          }
        };
      })(this);
      xhr.onerror = (function(_this) {
        return function() {
          if (files[0].status === Dropzone.CANCELED) {
            return;
          }
          return handleError();
        };
      })(this);
      progressObj = (_ref = xhr.upload) != null ? _ref : xhr;
      progressObj.onprogress = updateProgress;
      headers = {
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "X-Requested-With": "XMLHttpRequest"
      };
      if (this.options.headers) {
        extend(headers, this.options.headers);
      }
      for (headerName in headers) {
        headerValue = headers[headerName];
        xhr.setRequestHeader(headerName, headerValue);
      }
      formData = new FormData();
      if (this.options.params) {
        _ref1 = this.options.params;
        for (key in _ref1) {
          value = _ref1[key];
          formData.append(key, value);
        }
      }
      for (_j = 0, _len1 = files.length; _j < _len1; _j++) {
        file = files[_j];
        this.emit("sending", file, xhr, formData);
      }
      if (this.options.uploadMultiple) {
        this.emit("sendingmultiple", files, xhr, formData);
      }
      if (this.element.tagName === "FORM") {
        _ref2 = this.element.querySelectorAll("input, textarea, select, button");
        for (_k = 0, _len2 = _ref2.length; _k < _len2; _k++) {
          input = _ref2[_k];
          inputName = input.getAttribute("name");
          inputType = input.getAttribute("type");
          if (input.tagName === "SELECT" && input.hasAttribute("multiple")) {
            _ref3 = input.options;
            for (_l = 0, _len3 = _ref3.length; _l < _len3; _l++) {
              option = _ref3[_l];
              if (option.selected) {
                formData.append(inputName, option.value);
              }
            }
          } else if (!inputType || ((_ref4 = inputType.toLowerCase()) !== "checkbox" && _ref4 !== "radio") || input.checked) {
            formData.append(inputName, input.value);
          }
        }
      }
      for (i = _m = 0, _ref5 = files.length - 1; 0 <= _ref5 ? _m <= _ref5 : _m >= _ref5; i = 0 <= _ref5 ? ++_m : --_m) {
        formData.append(this._getParamName(i), files[i], files[i].name);
      }
      return xhr.send(formData);
    };

    Dropzone.prototype._finished = function(files, responseText, e) {
      var file, _i, _len;
      for (_i = 0, _len = files.length; _i < _len; _i++) {
        file = files[_i];
        file.status = Dropzone.SUCCESS;
        this.emit("success", file, responseText, e);
        this.emit("complete", file);
      }
      if (this.options.uploadMultiple) {
        this.emit("successmultiple", files, responseText, e);
        this.emit("completemultiple", files);
      }
      if (this.options.autoProcessQueue) {
        return this.processQueue();
      }
    };

    Dropzone.prototype._errorProcessing = function(files, message, xhr) {
      var file, _i, _len;
      for (_i = 0, _len = files.length; _i < _len; _i++) {
        file = files[_i];
        file.status = Dropzone.ERROR;
        this.emit("error", file, message, xhr);
        this.emit("complete", file);
      }
      if (this.options.uploadMultiple) {
        this.emit("errormultiple", files, message, xhr);
        this.emit("completemultiple", files);
      }
      if (this.options.autoProcessQueue) {
        return this.processQueue();
      }
    };

    return Dropzone;

  })(Em);

  Dropzone.version = "3.10.2";

  Dropzone.options = {};

  Dropzone.optionsForElement = function(element) {
    if (element.getAttribute("id")) {
      return Dropzone.options[camelize(element.getAttribute("id"))];
    } else {
      return void 0;
    }
  };

  Dropzone.instances = [];

  Dropzone.forElement = function(element) {
    if (typeof element === "string") {
      element = document.querySelector(element);
    }
    if ((element != null ? element.dropzone : void 0) == null) {
      throw new Error("No Dropzone found for given element. This is probably because you're trying to access it before Dropzone had the time to initialize. Use the `init` option to setup any additional observers on your Dropzone.");
    }
    return element.dropzone;
  };

  Dropzone.autoDiscover = true;

  Dropzone.discover = function() {
    var checkElements, dropzone, dropzones, _i, _len, _results;
    if (document.querySelectorAll) {
      dropzones = document.querySelectorAll(".dropzone");
    } else {
      dropzones = [];
      checkElements = function(elements) {
        var el, _i, _len, _results;
        _results = [];
        for (_i = 0, _len = elements.length; _i < _len; _i++) {
          el = elements[_i];
          if (/(^| )dropzone($| )/.test(el.className)) {
            _results.push(dropzones.push(el));
          } else {
            _results.push(void 0);
          }
        }
        return _results;
      };
      checkElements(document.getElementsByTagName("div"));
      checkElements(document.getElementsByTagName("form"));
    }
    _results = [];
    for (_i = 0, _len = dropzones.length; _i < _len; _i++) {
      dropzone = dropzones[_i];
      if (Dropzone.optionsForElement(dropzone) !== false) {
        _results.push(new Dropzone(dropzone));
      } else {
        _results.push(void 0);
      }
    }
    return _results;
  };

  Dropzone.blacklistedBrowsers = [/opera.*Macintosh.*version\/12/i];

  Dropzone.isBrowserSupported = function() {
    var capableBrowser, regex, _i, _len, _ref;
    capableBrowser = true;
    if (window.File && window.FileReader && window.FileList && window.Blob && window.FormData && document.querySelector) {
      if (!("classList" in document.createElement("a"))) {
        capableBrowser = false;
      } else {
        _ref = Dropzone.blacklistedBrowsers;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          regex = _ref[_i];
          if (regex.test(navigator.userAgent)) {
            capableBrowser = false;
            continue;
          }
        }
      }
    } else {
      capableBrowser = false;
    }
    return capableBrowser;
  };

  without = function(list, rejectedItem) {
    var item, _i, _len, _results;
    _results = [];
    for (_i = 0, _len = list.length; _i < _len; _i++) {
      item = list[_i];
      if (item !== rejectedItem) {
        _results.push(item);
      }
    }
    return _results;
  };

  camelize = function(str) {
    return str.replace(/[\-_](\w)/g, function(match) {
      return match.charAt(1).toUpperCase();
    });
  };

  Dropzone.createElement = function(string) {
    var div;
    div = document.createElement("div");
    div.innerHTML = string;
    return div.childNodes[0];
  };

  Dropzone.elementInside = function(element, container) {
    if (element === container) {
      return true;
    }
    while (element = element.parentNode) {
      if (element === container) {
        return true;
      }
    }
    return false;
  };

  Dropzone.getElement = function(el, name) {
    var element;
    if (typeof el === "string") {
      element = document.querySelector(el);
    } else if (el.nodeType != null) {
      element = el;
    }
    if (element == null) {
      throw new Error("Invalid `" + name + "` option provided. Please provide a CSS selector or a plain HTML element.");
    }
    return element;
  };

  Dropzone.getElements = function(els, name) {
    var e, el, elements, _i, _j, _len, _len1, _ref;
    if (els instanceof Array) {
      elements = [];
      try {
        for (_i = 0, _len = els.length; _i < _len; _i++) {
          el = els[_i];
          elements.push(this.getElement(el, name));
        }
      } catch (_error) {
        e = _error;
        elements = null;
      }
    } else if (typeof els === "string") {
      elements = [];
      _ref = document.querySelectorAll(els);
      for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
        el = _ref[_j];
        elements.push(el);
      }
    } else if (els.nodeType != null) {
      elements = [els];
    }
    if (!((elements != null) && elements.length)) {
      throw new Error("Invalid `" + name + "` option provided. Please provide a CSS selector, a plain HTML element or a list of those.");
    }
    return elements;
  };

  Dropzone.confirm = function(question, accepted, rejected) {
    if (window.confirm(question)) {
      return accepted();
    } else if (rejected != null) {
      return rejected();
    }
  };

  Dropzone.isValidFile = function(file, acceptedFiles) {
    var baseMimeType, mimeType, validType, _i, _len;
    if (!acceptedFiles) {
      return true;
    }
    acceptedFiles = acceptedFiles.split(",");
    mimeType = file.type;
    baseMimeType = mimeType.replace(/\/.*$/, "");
    for (_i = 0, _len = acceptedFiles.length; _i < _len; _i++) {
      validType = acceptedFiles[_i];
      validType = validType.trim();
      if (validType.charAt(0) === ".") {
        if (file.name.toLowerCase().indexOf(validType.toLowerCase(), file.name.length - validType.length) !== -1) {
          return true;
        }
      } else if (/\/\*$/.test(validType)) {
        if (baseMimeType === validType.replace(/\/.*$/, "")) {
          return true;
        }
      } else {
        if (mimeType === validType) {
          return true;
        }
      }
    }
    return false;
  };

  if (typeof jQuery !== "undefined" && jQuery !== null) {
    jQuery.fn.dropzone = function(options) {
      return this.each(function() {
        return new Dropzone(this, options);
      });
    };
  }

  if (typeof module !== "undefined" && module !== null) {
    module.exports = Dropzone;
  } else {
    window.Dropzone = Dropzone;
  }

  Dropzone.ADDED = "added";

  Dropzone.QUEUED = "queued";

  Dropzone.ACCEPTED = Dropzone.QUEUED;

  Dropzone.UPLOADING = "uploading";

  Dropzone.PROCESSING = Dropzone.UPLOADING;

  Dropzone.CANCELED = "canceled";

  Dropzone.ERROR = "error";

  Dropzone.SUCCESS = "success";


  /*

  Bugfix for iOS 6 and 7
  Source: http://stackoverflow.com/questions/11929099/html5-canvas-drawimage-ratio-bug-ios
  based on the work of https://github.com/stomita/ios-imagefile-megapixel
   */

  detectVerticalSquash = function(img) {
    var alpha, canvas, ctx, data, ey, ih, iw, py, ratio, sy;
    iw = img.naturalWidth;
    ih = img.naturalHeight;
    canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = ih;
    ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    data = ctx.getImageData(0, 0, 1, ih).data;
    sy = 0;
    ey = ih;
    py = ih;
    while (py > sy) {
      alpha = data[(py - 1) * 4 + 3];
      if (alpha === 0) {
        ey = py;
      } else {
        sy = py;
      }
      py = (ey + sy) >> 1;
    }
    ratio = py / ih;
    if (ratio === 0) {
      return 1;
    } else {
      return ratio;
    }
  };

  drawImageIOSFix = function(ctx, img, sx, sy, sw, sh, dx, dy, dw, dh) {
    var vertSquashRatio;
    vertSquashRatio = detectVerticalSquash(img);
    return ctx.drawImage(img, sx, sy, sw, sh, dx, dy, dw, dh / vertSquashRatio);
  };


  /*
   * contentloaded.js
   *
   * Author: Diego Perini (diego.perini at gmail.com)
   * Summary: cross-browser wrapper for DOMContentLoaded
   * Updated: 20101020
   * License: MIT
   * Version: 1.2
   *
   * URL:
   * http://javascript.nwbox.com/ContentLoaded/
   * http://javascript.nwbox.com/ContentLoaded/MIT-LICENSE
   */

  contentLoaded = function(win, fn) {
    var add, doc, done, init, poll, pre, rem, root, top;
    done = false;
    top = true;
    doc = win.document;
    root = doc.documentElement;
    add = (doc.addEventListener ? "addEventListener" : "attachEvent");
    rem = (doc.addEventListener ? "removeEventListener" : "detachEvent");
    pre = (doc.addEventListener ? "" : "on");
    init = function(e) {
      if (e.type === "readystatechange" && doc.readyState !== "complete") {
        return;
      }
      (e.type === "load" ? win : doc)[rem](pre + e.type, init, false);
      if (!done && (done = true)) {
        return fn.call(win, e.type || e);
      }
    };
    poll = function() {
      var e;
      try {
        root.doScroll("left");
      } catch (_error) {
        e = _error;
        setTimeout(poll, 50);
        return;
      }
      return init("poll");
    };
    if (doc.readyState !== "complete") {
      if (doc.createEventObject && root.doScroll) {
        try {
          top = !win.frameElement;
        } catch (_error) {}
        if (top) {
          poll();
        }
      }
      doc[add](pre + "DOMContentLoaded", init, false);
      doc[add](pre + "readystatechange", init, false);
      return win[add](pre + "load", init, false);
    }
  };

  Dropzone._autoDiscoverFunction = function() {
    if (Dropzone.autoDiscover) {
      return Dropzone.discover();
    }
  };

  contentLoaded(window, Dropzone._autoDiscoverFunction);

}).call(this);

});

if (typeof exports == "object") {
  module.exports = require("dropzone");
} else if (typeof define == "function" && define.amd) {
  define([], function(){ return require("dropzone"); });
} else {
  this["Dropzone"] = require("dropzone");
}
})()

/**
 * Treebeard : hierarchical grid built with Mithril
 * https://github.com/caneruguz/treebeard
 * Built by Center for Open Science -> http://www.cos.io
 */
;  // jshint ignore:line
(function (global, factory) {
    "use strict";
    var m;
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jQuery', 'mithril'], factory);
    } else if (typeof exports === 'object') {
        // If using webpack, load CSS with it
        if (typeof webpackJsonp !== 'undefined') {
            // NOTE: Assumes that the style-loader and css-loader are used for .css files
            require('./treebeard.css');
        }
        // Node. Does not work with strict CommonJS, but
        // only CommonJS-like environments that support module.exports,
        // like Node.
        m = require('mithril');
        module.exports = factory(jQuery, m);
    } else {
        // Browser globals (root is window)
        m = global.m;
        global.Treebeard = factory(jQuery, m);
    }
}(this, function(jQuery, m) {
    "use strict";

    //Force cache busting in IE
    var oldmrequest = m.request;
    m.request = function () {
        var buster;
        var requestArgs = arguments[0];
        if (requestArgs.url.indexOf('?') !== -1) {
            buster = '&_=';
        } else {
            buster = '?_=';
        }
        requestArgs.url += (buster + (new Date().getTime()));
        return oldmrequest.apply(this, arguments);
    };

    // From Underscore.js, MIT License
    //
    // Returns a function, that, as long as it continues to be invoked, will not
    // be triggered. The function will be called after it stops being called for
    // N milliseconds. If `immediate` is passed, trigger the function on the
    // leading edge, instead of the trailing.
    var debounce = function(func, wait, immediate) {
        var timeout, args, context, timestamp, result;

        var later = function() {
            var last = new Date().getTime() - timestamp;

            if (last < wait && last >= 0) {
                timeout = setTimeout(later, wait - last);
            } else {
                timeout = null;
                if (!immediate) {
                    result = func.apply(context, args);
                    if (!timeout) {
                        context = args = null;
                    }
                }
            }
        };

        return function() {
            context = this;
            args = arguments;
            timestamp = new Date().getTime();
            var callNow = immediate && !timeout;
            if (!timeout) {
                timeout = setTimeout(later, wait);
            }
            if (callNow) {
                result = func.apply(context, args);
                context = args = null;
            }

            return result;
        };
    };

    // Indexes by id, shortcuts to the tree objects. Use example: var item = Indexes[23];
    var Indexes = {},
        // Item constructor
        Item,
        // Notifications constructor
        Notify,
        // Modal for box-wide errors
        Modal,
        // Initialize and namespace Treebeard module
        Treebeard = {};
    // Create unique ids, we are now using our own ids. Data ids are availbe to user through tree.data
    // we are using globals here because of mithril views with unique keys for rows in case we have multiple
    // instances of treebeard on the same page.
    if (!window.treebeardCounter) {
        window.treebeardCounter = -1;
    }

    /**
     * Gets the incremented idCounter as a unique id
     * @returns {Number} idCounter The state of id counter after incementing
     */
    function getUID() {
        window.treebeardCounter = window.treebeardCounter + 1;
        return window.treebeardCounter;
    }

    /**
     * Checks whether the argument passed is a string or function, useful for allowing different types of options to be set
     * @param {Mixed} x Argument passed, can be anything
     * @returns {Mixed} x If x is a function returns the execution, otherwise returns x as it is, expecting it to be a string.
     */
    function functionOrString(x) {
        if (!x) {
            return "";
        }
        if ($.isFunction(x)) {
            return x();
        }
        return x;
    }

    /**
     * Sorts ascending based on any attribute on data
     * @param {String} data The property of the object to be checked for comparison
     * @param {String} sortType Whether sort is pure numbers of alphanumerical,
     * @returns {Number} result The result of the comparison function, 0 for equal, -1 or 1 for one is bigger than other.
     */
    function ascByAttr(data, sortType) {
        if (sortType === "number") {
            return function _numCompare(a, b) {
                var num1 = a.data[data] ? a.data[data] : 0;
                var num2 = b.data[data] ? b.data[data] : 0;
                var compareNum = num1 - num2;
                if(compareNum === 0) return a.id - b.id;
                return compareNum;
            };
        }
        if (sortType === 'date') {
            return function _dateCompare(a, b) {
                var date1 = a.data[data] ? new Date(a.data[data]) : new Date(0);
                var date2 = b.data[data] ? new Date(b.data[data]) : new Date(0);
                var compareDates = date1 - date2;
                if(compareDates === 0) return a.id - b.id;
                return compareDates;
            };
        }
        return function _compare(a, b) {
            var textA = a.data[data] ? a.data[data].toString().toLowerCase().replace(/\s/g, '').trim() : '',
                textB = b.data[data] ? b.data[data].toString().toLowerCase().replace(/\s/g, '').trim() : '';
            if (textA < textB) {
                return -1;
            }
            if (textA > textB) {
                return 1;
            }
            return a.id < b.id ? -1 : +1;
        };
    }

    /**
     * Sorts descending based on any attribute on data
     * @param {String} data The property of the object to be checked for comparison
     * @param {String} sortType Whether sort is pure numbers of alphanumerical,
     * @returns {Number} result The result of the comparison function, 0 for equal, -1 or 1 for one is bigger than other.
     */
    function descByAttr(data, sortType) {
        if (sortType === "number") {
            return function _numCompare(a, b) {
                var num1 = a.data[data] ? a.data[data] : 0;
                var num2 = b.data[data] ? b.data[data] : 0;
                var compareNum = num2 - num1;
                if(compareNum === 0) return b.id - a.id;
                return compareNum;
            };
        }
        if (sortType === 'date') {
            return function _dateCompare(a, b) {
                var date1 = a.data[data] ? new Date(a.data[data]) : new Date(0);
                var date2 = b.data[data] ? new Date(b.data[data]) : new Date(0);
                var compareDates = date2 - date1;
                if(compareDates === 0) return b.id - a.id;
                return compareDates;
            };
        }
        return function _compare(a, b) {
            var textA = a.data[data] ? a.data[data].toString().toLowerCase().replace(/\s/g, '') : '',
                textB = b.data[data] ? b.data[data].toString().toLowerCase().replace(/\s/g, '') : '';
            if (textA > textB) {
                return -1;
            }
            if (textA < textB) {
                return 1;
            }
            return a.id > b.id ? -1 : +1;
        };
    }

    /**
     * Helper function that removes an item from an array of items based on the value of an attribute of that item
     * @param {Array} arr The array that item needs to be removed from
     * @param {String} attr The property based on which the removal should happen
     * @param {String} value The value that needs to match the property for removal to happen
     * @returns {Boolean} done Whether the remove was successful.
     */
    function removeByProperty(arr, attr, value) {
        var i,
            done = false;
        for (i = 0; i < arr.length; i++) {
            if (arr[i] && arr[i].hasOwnProperty(attr) && (arguments.length > 2 && arr[i][attr] === value)) {
                arr.splice(i, 1);
                done = true;
                return done;
            }
        }
        return done;
    }

    var DEFAULT_NOTIFY_TIMEOUT = 3000;
    /**
     * Implementation of a notification system, added to each row
     * @param {String} [message] Notification message
     * @param {String} [type] One of the bootstrap alert types (info, danger, warning, success, primary, default)
     * @param {Number} [column] Which column the message should replace, if empty the entire row will be used
     * @param {Number} [timeout] Milliseconds that takes for message to be removed.
     * @constructor
     */
    Notify = function _notify(message, type, column, timeout) {
        this.column = column || null;
        this.type = type || "info";
        this.message = message || 'Hello';
        this.on = false;
        this.timeout = timeout === undefined ? DEFAULT_NOTIFY_TIMEOUT : timeout;
        this.css = '';
        this.toggle = function () {
            this.on = !this.on;
        };
        this.show = function () {
            this.on = true;
            var self = this;
            if (self.timeout && self.timeout > 1) { // set timeout to 1 to stay forever
                setTimeout(function () {
                    self.hide();
                }, self.timeout);
            }
            m.redraw(true);
        };
        this.hide = function () {
            this.on = false;
            m.redraw(true);
        };
        this.update = function (message, type, column, timeout, css) {
            this.type = type || this.type;
            this.column = column || this.column;
            this.timeout = timeout === undefined ? DEFAULT_NOTIFY_TIMEOUT : timeout;
            this.message = message;
            this.css = css || '';
            this.show(true);
        };
        this.selfDestruct = function (treebeard, item, timeout) {
            this.on = false;
            this.on = true;
            var self = this,
                out = timeout || 3000;
            setTimeout(function () {
                self.hide();
                item.removeSelf();
                treebeard.redraw();
            }, out);
        };
    };

    /**
     * Implementation of a modal system, currently used once sitewide
     * @constructor
     */
    Modal = function _modal(ctrl) {
        var el = ctrl.select('#tb-tbody'),
            self = this;
        this.on = false;
        this.timeout = false;
        this.css = '';
        this.padding = '50px 100px;';
        this.header = null;
        this.content = null;
        this.actions = null;
        this.height = el.height();
        this.width = el.width();
        this.dismiss = function () {
            this.on = false;
            m.redraw(true);
            ctrl.select('#tb-tbody').css('overflow', 'auto');
        };
        this.show = function () {
            this.on = true;
            if (self.timeout) {
                setTimeout(function () {
                    self.dismiss();
                }, self.timeout);
            }
            m.redraw(true);
        };
        this.toggle = function () {
            this.on = !this.on;
            m.redraw(true);
        };
        this.update = function (contentMithril, actions, header) {
            self.updateSize();
            if (header) {
                this.header = header;
            }
            if (contentMithril) {
                this.content = contentMithril;
            }
            if (actions) {
                this.actions = actions;
            }
            this.on = true;
            m.redraw(true);
        };

        this.updateSize = function () {
            this.height = ctrl.select('#tb-tbody').height();
            this.width = ctrl.select('#tb-tbody').width();
            if (this.width < 500) {
                this.padding = '40px';
            } else {
                this.padding = '50px 100px';
            }
            m.redraw(true);
        };
        this.onmodalshow = function () {
            var margin = ctrl.select('#tb-tbody').scrollTop();
            ctrl.select('.tb-modal-shade').css('margin-top', margin);
            ctrl.select('#tb-tbody').css('overflow', 'hidden');
        };
        $(window).resize(function () {
            self.updateSize();
        });
    };

    /**
     * Builds an _item that uses item related api calls, what we mean when we say "constructed by _item"
     * @param {Object} data Raw data to be converted into an item
     * @returns {Object} this Returns itself with the new properties.
     * @constructor
     */
    Item = function _item(data) {
        if (data === undefined) {
            this.data = {};
            this.kind = "folder";
            this.open = true;
        } else {
            this.data = data;
            this.kind = data.kind || "file";
            this.open = data.open;
        }
        if (this.kind === 'folder') {
            this.load = false;
        }
        this.id = getUID();
        this.depth = 0;
        this.children = [];
        this.parentID = null;
        this.notify = new Notify();
    };

    /**
     * Add a child item into the item and correctly assign depth and other properties
     * @param {Object} component Item created with cosntructor _item, missing depth information
     * @param {Boolean} [toTop] Whether the item should be added to the top or bottom of children array
     * @returns {Object} this The current item.
     */
    Item.prototype.add = function _itemAdd(component, toTop) {
        component.parentID = this.id;
        component.depth = this.depth + 1;
        component.open = false;
        component.load = false;
        if (component.depth > 1 && component.children.length === 0) {
            component.open = false;
        }
        if (toTop) {
            this.children.unshift(component);
        } else {
            this.children.push(component);
        }
        return this;
    };

    /**
     * Move item from one place to another within the tree
     * @param {Number} toID Unique id of the container item to move to
     * @returns {Object} this The current item.
     */
    Item.prototype.move = function _itemMove(toID, toTop) {
        var toItem = Indexes[toID],
            parentID = this.parentID,
            parent = Indexes[parentID];
        toItem.add(this, toTop);
        toItem.redoDepth();
        if (parentID > -1) {
            parent.removeChild(parseInt(this.id, 10));
        }
        return this;
    };

    /**
     * Reassigns depth information when tree manipulations happen so depth remains accurate within object descendants
     */
    Item.prototype.redoDepth = function _itemRedoDepth() {
        function recursive(items, depth) {
            var i;
            for (i = 0; i < items.length; i++) {
                items[i].depth = depth;
                if (items[i].children.length > 0) {
                    recursive(items[i].children, depth + 1);
                }
            }
        }
        recursive(this.children, this.depth + 1);
    };

    /**
     * Deletes itself
     * @param {Number} childID Id of the child inside this item
     * @returns {Object} parent The parent of the removed item
     */
    Item.prototype.removeSelf = function _itemRemoveSelf() {
        var parent = this.parent();
        parent.removeChild(this.id);
        return parent;
    };

    /**
     * Deletes child from item by unique id
     * @param {Number} childID Id of the child inside this item
     * @returns {Object} this The item containing the child
     */
    Item.prototype.removeChild = function _itemRemoveChild(childID) {
        removeByProperty(this.children, 'id', childID);
        return this;
    };

    /**
     * Returns next sibling based on position in the parent list
     * @returns {Object} next The next object constructed by _item
     */
    Item.prototype.next = function _itemNext() {
        var next, parent, i;
        parent = Indexes[this.parentID];
        for (i = 0; i < parent.children.length; i++) {
            if (parent.children[i].id === this.id) {
                next = parent.children[i + 1];
                return next;
            }
        }
        if (!next) {
            throw new Error("Treebeard Error: Item with ID '" + this.id + "' has no next sibling");
        }
    };

    /**
     * Returns previous sibling based on position in the parent list
     * @returns {Object} prev The previous object constructed by _item
     */
    Item.prototype.prev = function _itemPrev() {
        var prev, parent, i;
        parent = Indexes[this.parentID];
        for (i = 0; i < parent.children.length; i++) {
            if (parent.children[i].id === this.id) {
                prev = parent.children[i - 1];
                return prev;
            }
        }
        if (!prev) {
            throw new Error("Treebeard Error: Item with ID '" + this.id + "' has no previous sibling");
        }
    };

    /**
     * Returns single child based on id
     * @param {Number} childID Id of the child inside this item
     * @returns {Object} child The child object constructed by _item
     */
    Item.prototype.child = function _itemChild(childID) {
        var child, i;
        for (i = 0; i < this.children.length; i++) {
            if (this.children[i].id === childID) {
                child = this.children[i];
                return child;
            }
        }
        if (!child) {
            throw new Error("Treebeard Error: Parent with ID '" + this.id + "' has no child with ID: " + childID);
        }
    };

    /**
     * Returns parent of the item one level above
     * @returns {Object} parent The parent object constructed by _item
     */
    Item.prototype.parent = function _itemParent() {
        if (Indexes[this.parentID]) {
            return Indexes[this.parentID];
        }
        return undefined;
    };

    /**
     * Sorts children of the item by direction and selected field.
     * @param {Object} treebeard The instance of the treebeard controller being used
     * @param {String} direction Sort direction, can be 'asc' or 'desc'
     * @param {String} sortType Whether the sort type is number or alphanumeric
     * @param {Number} index The index of the column, needed to find out which field to be sorted
     */
    Item.prototype.sortChildren = function _itemSort(treebeard, direction, sortType, index, sortDepth) {
        var columns = treebeard.options.resolveRows.call(treebeard, this),
            field = columns[index].data;
        if (!direction || (direction !== 'asc' && direction !== 'desc')) {
            throw new Error("Treebeard Error: To sort children you need to pass direction as asc or desc to Item.sortChildren");
        }
        if (this.depth >= sortDepth && this.children.length > 0) {
            if (direction === "asc") {
                this.children.sort(ascByAttr(field, sortType));
            }
            if (direction === "desc") {
                this.children.sort(descByAttr(field, sortType));
            }
        }
    };

    /**
     * Checks if item is ancestor (contains) of another item passed as argument
     * @param {Object} item An item constructed by _item
     * @returns {Boolean} result Whether the item is ancestor of item passed as argument
     */
    Item.prototype.isAncestor = function _isAncestor(item) {
        function _checkAncestor(a, b) {
            if (a.id === b.id) {
                return true;
            }
            if (a.parent()) {
                return _checkAncestor(a.parent(), b);
            }
            return false;
        }
        if (item.parent()) {
            return _checkAncestor(item.parent(), this);
        }
        return false;
    };

    /**
     * Checks if item is descendant (a child) of another item passed as argument
     * @param {Object} item An item constructed by _item
     * @returns {Boolean} result Whether the item is descendant of item passed as argument
     */
    Item.prototype.isDescendant = function(item) {
        var i,
            result = false;

        function _checkDescendant(children, b) {
            for (i = 0; i < children.length; i++) {
                if (children[i].id === b.id) {
                    result = true;
                    break;
                }
                if (children[i].children.length > 0) {
                    return _checkDescendant(children[i].children, b);
                }
            }
            return result;
        }
        return _checkDescendant(item.children, this);
    };

    // Treebeard methods
    Treebeard.controller = function _treebeardController(opts) {
        // private variables
        var self = this; // Treebard.controller
		var filesDropArray = [];
		var filesCompleteArray = [];
		var filesSuccessArray = [];
		var filesFailedArray = [];
        var lastLocation = 0; // The last scrollTop location, updates on every scroll.
        var lastNonFilterLocation = 0; // The last scrolltop location before filter was used.
        this.isSorted = {}; // Temporary variables for sorting
        m.redraw.strategy("all");
        // public variables
        this.flatData = []; // Flat data, gets regenerated often
        this.treeData = {}; // The data in hierarchical form
        this.filterText = m.prop(""); // value of the filtertext input
        this.showRange = []; // Array of indexes that the range shows
        this.options = opts; // User defined options
        this.selected = undefined; // The row selected on click.
        this.rangeMargin = 0; // Top margin, required for proper scrolling
        this.visibleIndexes = []; // List of items viewable as a result of an operation like filter.
        this.visibleTop = undefined; // The first visible item.
        this.currentPage = m.prop(1); // for pagination
        this.dropzone = null; // Treebeard's own dropzone object
        this.dropzoneItemCache = undefined; // Cache of the dropped item
        this.filterOn = false; // Filter state for use across the app
        this.multiselected = m.prop([]);
        this.pressedKey = undefined;
        this.dragOngoing = false;
        this.initialized = false; // Treebeard's own initialization check, turns to true after page loads.
        this.colsizes = {}; // Storing column sizes across the app.
        this.tableWidth = m.prop('auto;'); // Whether there should be horizontal scrolling
        this.isUploading = m.prop(false); // Whether an upload is taking place.

        /**
         * Helper function to redraw if user makes changes to the item (like deleting through a hook)
         */
        this.redraw = function _redraw() {
            self.flatten(self.treeData.children, self.visibleTop);
        };

		this.refreshData = function _refreshData() {
			_loadData(self.options.filesData);
		}

        this.mredraw = function _mredraw() {
            m.redraw();
        }
        /**
         * Prepend selector with ID of root DOM node
         * @param {String} selector CSS selector
         */
        this.select = function (selector) {
            return $('#' + self.options.divID + ' ' + selector);
        };

        // Note: `Modal` constructor dependes on `controller#select`
        this.modal = new Modal(this);

        /**
         * Helper function to reset unique id to a reset number or -1
         * @param {Number} resetNum Number to reset counter to
         */
        this.resetCounter = function _resetCounter(resetNum) {
            if (resetNum !== 0) {
                window.treebeardCounter = resetNum || -1;
            } else {
                window.treebeardCounter = 0;
            }
        };

        /**
         * Instantiates draggable and droppable on DOM elements with options passed from self.options
         */
        this.initializeMove = function () {
            var self = this;
            var draggableOptions,
                droppableOptions,
                x,
                y;
            draggableOptions = {
                helper: 'clone',
                cursor: 'move',
                containment: '#' + self.options.divID,
                delay: 100,
                drag: function (event, ui) {
                    if (self.pressedKey === 27) {
                        return false;
                    }
                    if (self.options.dragEvents.drag) {
                        self.options.dragEvents.drag.call(self, event, ui);
                    } else {
                        if (self.dragText === "") {
                            if (self.multiselected().length > 1) {
                                var newHTML = $(ui.helper).text() + ' <b> + ' + (self.multiselected().length - 1) + ' more </b>';
                                self.dragText = newHTML;
                                $('.tb-drag-ghost').html(newHTML);
                            }
                        }
                        $(ui.helper).css({
                            display: 'none'
                        });
                    }
                    // keep copy of the element and attach it to the mouse location
                    x = event.pageX > 50 ? event.pageX - 50 : 50;
                    y = event.pageY - 10;
                    $('.tb-drag-ghost').css({
                        'position': 'absolute',
                        top: y,
                        left: x,
                        'height': '25px',
                        'width': '400px',
                        'background': 'white',
                        'padding': '0px 10px',
                        'box-shadow': '0 0 4px #ccc'
                    });
                },
                create: function (event, ui) {
                    if (self.options.dragEvents.create) {
                        self.options.dragEvents.create.call(self, event, ui);
                    }
                },
                start: function (event, ui) {
                    var thisID,
                        item,
                        ghost;
                    // if the item being dragged is not in multiselect clear multiselect
                    thisID = parseInt($(ui.helper).closest('.tb-row').attr('data-id'), 10);
                    item = self.find(thisID);
                    if (!self.isMultiselected(thisID)) {
                        self.clearMultiselect();
                        self.multiselected().push(item);
                    }
                    self.dragText = '';
                    ghost = $(ui.helper).clone();
                    ghost.addClass('tb-drag-ghost');
                    $('body').append(ghost);
                    if (self.options.dragEvents.start) {
                        self.options.dragEvents.start.call(self, event, ui);
                    }
                    self.dragOngoing = true;
                    self.select('.tb-row').removeClass(self.options.hoverClass + ' tb-h-error tb-h-success');
                },
                stop: function (event, ui) {
                    $('.tb-drag-ghost').remove();
                    if (self.options.dragEvents.stop) {
                        self.options.dragEvents.stop.call(self, event, ui);
                    }
                    self.dragOngoing = false;
                    self.select('.tb-row').removeClass(self.options.hoverClass + ' tb-h-error tb-h-success');
                }
            };

            droppableOptions = {
                tolerance: 'pointer',
                activate: function (event, ui) {
                    if (self.options.dropEvents.activate) {
                        self.options.dropEvents.activate.call(self, event, ui);
                    }
                },
                create: function (event, ui) {
                    if (self.options.dropEvents.create) {
                        self.options.dropEvents.create.call(self, event, ui);
                    }
                },
                deactivate: function (event, ui) {
                    if (self.options.dropEvents.deactivate) {
                        self.options.dropEvents.deactivate.call(self, event, ui);
                    }
                },
                drop: function (event, ui) {
                    if (self.options.dropEvents.drop) {
                        self.options.dropEvents.drop.call(self, event, ui);
                    }
                },
                out: function (event, ui) {
                    if (self.options.dropEvents.out) {
                        self.options.dropEvents.out.call(self, event, ui);
                    }
                },
                over: function (event, ui) {
                    var id = parseInt($(event.target).closest('.tb-row').attr('data-id'), 10);
                    self.scrollEdges(id);
                    if (self.options.dropEvents.over) {
                        self.options.dropEvents.over.call(self, event, ui);
                    }
                }
            };
            self.options.finalDragOptions = $.extend(draggableOptions, self.options.dragOptions);
            self.options.finalDropOptions = $.extend(droppableOptions, self.options.dropOptions);
            self.options.dragSelector = self.options.moveClass || 'td-title';
            self.moveOn();
        };

        // Handles scrolling when items are at the beginning or end of visible items.
        this.scrollEdges = function (id, buffer) {
            var buffer = buffer || 1,
                last = self.flatData[self.showRange[self.showRange.length - 1 - buffer]].id,
                first = self.flatData[self.showRange[0 + buffer]].id,
                currentScroll = self.select('#tb-tbody').scrollTop();
            if (id === last) {
                self.select('#tb-tbody').scrollTop(currentScroll + self.options.rowHeight + 1);
            }
            if (id === first) {
                self.select('#tb-tbody').scrollTop(currentScroll - self.options.rowHeight - 1);
            }
        }

        /**
         * Turns move on for all elements or elements within a parent container
         * @param parent DOM element for parent
         */
        this.moveOn = function _moveOn(parent) {
            if (!parent) {
                self.select('.' + self.options.dragSelector).draggable(self.options.finalDragOptions);
                self.select('.tb-row').droppable(self.options.finalDropOptions);
            } else {
                $(parent).find('.' + self.options.dragSelector).draggable(self.options.finalDragOptions);
                $(parent).droppable(self.options.finalDropOptions);
            }
        };

        /**
         * Removes move related instances by destroying draggable and droppable.
         */
        this.moveOff = function _moveOff() {
            self.select('.td-title').draggable('destroy');
            self.select('.tb-row').droppable('destroy');
        };

        /**
         * Deletes item from tree and refreshes view
         * @param {Number} parentID Unique id of the parent
         * @param {Number} itemID Unique id of the item
         * @returns {Object} A shallow copy of the item that was just deleted.
         */
        this.deleteNode = function _deleteNode(parentID, itemID) { // TODO : May be redundant to include parentID
            var item = Indexes[itemID],
                itemcopy = $.extend({}, item);
            $.when(self.options.deletecheck.call(self, item)).done(function _resolveDeleteCheck(check) {
                if (check) {
                    var parent = Indexes[parentID];
                    parent.removeChild(itemID);
                    self.flatten(self.treeData.children, self.visibleTop);
                    if (self.options.ondelete) {
                        self.options.ondelete.call(self, itemcopy);
                    }
                }
            });
            return itemcopy;
        };

        /**
         * Checks if a move between items can be done based on logic of which contains the other
         * @param {Object} toItem Receiving item data constructed by _item
         * @param {Object} parentID Item to be moved as constructed by _item
         * @returns {Boolean} Whether the move can be done or not
         */
        this.canMove = function _canMove(toItem, fromItem) {
            // is toItem a folder?
            if (toItem.kind !== "folder") {
                return false;
            }
            // is toItem a descendant of fromItem?
            if (toItem.isDescendant(fromItem)) {
                return false;
            }
            return true;
        };

        /**
         * Adds an item to the list with proper tree and flat data and view updates
         * @param {Object} item the raw data of the item
         * @param {Number} parentID the unique id of the parent object the item should be added to
         * @returns {Object} newItem the created item as constructed by _item with correct parent information.
         */
        this.createItem = function _createItem(item, parentID) {
            var parent = Indexes[parentID],
                newItem;
            $.when(self.options.createcheck.call(self, item, parent)).done(function _resolveCreateCheck(check) {
                if (check) {
                    newItem = new Item(item);
                    parent.add(newItem, true);
                    self.flatten(self.treeData.children, self.visibleTop);
                    if (self.options.oncreate) {
                        self.options.oncreate.call(self, newItem, parent);
                    }
                } else {
                    throw new Error('Treebeard Error: createcheck function returned false, item not created.');
                }
            });
            return newItem;
        };

        /**
         * Finds the entire item object through the id only
         * @param {Number} id Unique id of the item acted on
         * @returns {Number} _item The full item object constructed by _item.
         */
        this.find = function _find(id) {
            if (Indexes[id]) {
                return Indexes[id];
            }
            return undefined;
        };

        /**
         * Returns the index of an item in the flat row list (self.flatData)
         * @param {Number} id Unique id of the item acted on (usually item.id) .
         * @returns {Number} i The index at which the item is found or undefined if nothing is found.
         */
        this.returnIndex = function _returnIndex(id) {
            var len = self.flatData.length,
                i, o;
            for (i = 0; i < len; i++) {
                o = self.flatData[i];
                if (o.id === id) {
                    return i;
                }
            }
            return undefined;
        };

        /**
         * Returns the index of an item in the showRange list (self.showRange)
         * @param {Number} id Unique id of the item acted on (usually item.id) .
         * @returns {Number} i The index at which the item is found or undefined if nothing is found.
         */
        this.returnRangeIndex = function _returnRangeIndex(id) {
            var len = self.showRange.length,
                i, o;
            for (i = 0; i < len; i++) {
                o = self.flatData[self.showRange[i]];
                if (o.id === id) {
                    return i;
                }
            }
            return undefined;
        };

        /**
         * Returns whether a single row contains the filtered items, checking if columns can be filtered
         * @param {Object} item Item constructed with _item which the filtering is acting on.
         * @returns {Boolean} titleResult Whether text is found within the item, default is false;
         */
        this.rowFilterResult = function _rowFilterResult(item) {
            $('#tb-tbody').scrollTop(0);
            self.currentPage(1);
            var cols = self.options.resolveRows.call(self, item),
                filter = self.filterText().toLowerCase(),
                titleResult = false,
                i,
                j,
                o;
            for (i = 0; i < cols.length; i++) {
                o = cols[i];
                if (o.filter && item.data[o.data].toString().toLowerCase().indexOf(filter) !== -1) {
                    titleResult = true;
                }
            }
            var hiddenRows = self.options.hiddenFilterRows;
            if (hiddenRows && hiddenRows.length > 0){
                for (j = 0; j < hiddenRows.length; j++) {
                    if (item.data[hiddenRows[j]].toString().toLowerCase().indexOf(filter) !== -1) {
                        titleResult = true;
                    }
                }
            }
            return titleResult;
        };

        /**
         * Runs filter functions and resets depending on whether there is a filter word
         * @param {Event} e Event object fired by the browser
         * @config {Object} currentTarget Event object needs to have a e.currentTarget element object for mithril.
         */
        this.filter = function _filter(e) {
            m.withAttr("value", self.filterText)(e);
            var filter = self.filterText().toLowerCase(),
                index = self.visibleTop;
            if (filter.length === 0) {
                self.resetFilter();
            } else {
                if (!self.filterOn) {
                    self.filterOn = true;
                    self.lastNonFilterLocation = self.lastLocation;
                }
                if (!self.visibleTop) {
                    index = 0;
                }
                self.calculateVisible(index);
                self.calculateHeight();
                m.redraw(true);
                if (self.options.onfilter) {
                    self.options.onfilter.call(self, filter);
                }
            }
        };

        /**
         * Programatically cancels filtering
         */
        this.resetFilter = function _resetFilter(location) {
            var tb = this;
            var lastNonFilterLocation = location || self.lastNonFilterLocation;
            var filter = self.filterText().toLowerCase();
            tb.filterOn = false;
            tb.calculateVisible(0);
            tb.calculateHeight();
            m.redraw(true);
            self.select('#tb-tbody').scrollTop(lastNonFilterLocation); // restore location of scroll
            if (tb.options.onfilterreset) {
                tb.options.onfilterreset.call(tb, filter);
            }
        }


        /**
         * Updates content of the folder with new data or refreshes from lazyload
         * @param {Array} data New raw items, may be returned from ajax call
         * @param {Object} parent Item built with the _item constructor
         * @param {Function} callback A function to be called after loading all data
         */
        this.updateFolder = function (data, parent, callback, flatten) {
            if (data) {
                parent.children = [];
                var child, i;
                for (i = 0; i < data.length; i++) {
                    child = self.buildTree(data[i], parent);
                    parent.add(child);
                }
                parent.open = true;
                //return;
            }
            var index = self.returnIndex(parent.id);
            parent.open = false;
            parent.load = false;
            if(flatten){
                self.flatten(self.treeData.children, self.visibleTop);
            }
            self.toggleFolder(index, null, callback);
        };

        /**
         * Toggles folder, refreshing the view or reloading in event of lazyload
         * @param {Number} index The index of the item in the flatdata.
         * @param {Event} [event] Toggle click event if this function is triggered by an event.
         * @param {Function} callback A function to be called after loading all data
         */
        this.toggleFolder = function _toggleFolder(index, event, callback) {
            if (index === undefined || index === null) {
                self.redraw();
                return;
            }
            var len = self.flatData.length,
                tree = Indexes[self.flatData[index].id],
                item = self.flatData[index],
                child,
                skip = false,
                skipLevel = item.depth,
                level = item.depth,
                i,
                j,
                o,
                t,
                lazyLoad,
                icon = $('.tb-row[data-id="' + item.id + '"]').find('.tb-toggle-icon'),
                iconTemplate;
            if (icon.get(0)) {
                m.render(icon.get(0), self.options.resolveRefreshIcon());
            }
            $.when(self.options.resolveLazyloadUrl.call(self, tree)).done(function _resolveLazyloadDone(url) {
                lazyLoad = url;
                if (lazyLoad && item.row.kind === "folder" && tree.open === false && tree.load === false) {
                    tree.children = [];
                    m.request({
                        method: "GET",
                        url: lazyLoad,
                        config: self.options.xhrconfig
                    })
                        .then(function _getUrlBuildtree(value) {
                            if (!value) {
                                self.options.lazyLoadError.call(self, tree);
                                iconTemplate = self.options.resolveToggle.call(self, tree);
                                if (icon.get(0)) {
                                    m.render(icon.get(0), iconTemplate);
                                }
                            } else {
                                if (self.options.lazyLoadPreprocess) {
                                    value = self.options.lazyLoadPreprocess.call(self, value);
                                }
                                if (!$.isArray(value)) {
                                    value = value.data;
                                }
                                var isUploadItem = function(element) {
                                    return element.data.tmpID;
                                };
                                tree.children = tree.children.filter(isUploadItem);
                                for (i = 0; i < value.length; i++) {
                                    child = self.buildTree(value[i], tree);
                                    tree.add(child);
                                }
                                tree.open = true;
                                tree.load = true;
                                // this redundancy is important to get the proper state
                                iconTemplate = self.options.resolveToggle.call(self, tree);
                                if (icon.get(0)) {
                                    m.render(icon.get(0), iconTemplate);
                                }
                            }
                        }, function (info) {
                            self.options.lazyLoadError.call(self, tree);
                            iconTemplate = self.options.resolveToggle.call(self, tree);
                            if (icon.get(0)) {
                                    m.render(icon.get(0), iconTemplate);
                                }
                        })
                        .then(function _getUrlFlatten() {
                            self.flatten(self.treeData.children, self.visibleTop);
                            if (self.options.lazyLoadOnLoad) {
                                self.options.lazyLoadOnLoad.call(self, tree, event);
                            }
                            if (self.options.ontogglefolder) {
                                self.options.ontogglefolder.call(self, tree, event);
                            }
                            if (callback) {
                                callback.call(self, tree, event);
                            }
                        });

                } else {
                    for (j = index + 1; j < len; j++) {
                        o = self.flatData[j];
                        t = Indexes[self.flatData[j].id];
                        if (o.depth <= level) {
                            break;
                        }
                        if (skip && o.depth > skipLevel) {
                            continue;
                        }
                        if (o.depth === skipLevel) {
                            skip = false;
                        }
                        if (tree.open) { // closing
                            o.show = false;
                        } else { // opening
                            o.show = true;
                            if (!t.open) {
                                skipLevel = o.depth;
                                skip = true;
                            }
                        }
                    }
                    tree.open = !tree.open;
                    self.calculateVisible(self.visibleTop);
                    self.calculateHeight();
                    m.redraw(true);
                    var iconTemplate = self.options.resolveToggle.call(self, tree);
                    if (icon.get(0)) {
                        m.render(icon.get(0), iconTemplate);
                    }
                    if (self.options.ontogglefolder) {
                        self.options.ontogglefolder.call(self, tree, event);
                    }
                }
                if (self.options.allowMove) {
                    self.moveOn();
                }
            });
        };

        /**
         * Toggles the sorting when clicked on sort icons.
         * @param {Event} [event] Toggle click event if this function is triggered by an event.
         */
        this.sortToggle = function _isSortedToggle(ev, col, type, sortType) {
            var counter = 0;
            var redo;
            var element;
            if(ev){ // If a button is clicked, use the element attributes
                element = $(ev.target);
                type = element.attr('data-direction');
                col = parseInt(element.parent('.tb-th').attr('data-tb-th-col'));
                sortType = element.attr('data-sortType');
            }
            self.select('.asc-btn, .desc-btn').addClass('tb-sort-inactive'); // turn all styles off
            for(var column in self.isSorted) {
                self.isSorted[column].asc = false;
                self.isSorted[column].desc = false;
            }
            if (!self.isSorted[col][type]) {
                redo = function _redo(data) {
                    data.map(function _mapToggle(item) {
                        item.sortChildren(self, type, sortType, col, self.options.sortDepth);
                        if (item.children.length > 0) {
                            redo(item.children);
                        }
                        counter = counter + 1;
                    });
                };
                self.treeData.sortChildren(self, type, sortType, col, self.options.sortDepth); // Then start recursive loop
                redo(self.treeData.children);
                self.select('div[data-tb-th-col=' + col + ']').children('.' + type + '-btn').removeClass('tb-sort-inactive');
                self.isSorted[col][type] = true;
                self.flatten(self.treeData.children, 0);
            }
        };


        /**
         * Calculate how tall the wrapping div should be so that scrollbars appear properly
         * @returns {Number} itemsHeight Number of pixels calculated in the function for height
         */
        this.calculateHeight = function _calculateHeight() {
            var itemsHeight;
            if (!self.options.paginate) {
                itemsHeight = self.visibleIndexes.length * self.options.rowHeight;
            } else {
                itemsHeight = self.options.showTotal * self.options.rowHeight;
                self.rangeMargin = 0;
            }
            self.innerHeight = itemsHeight + self.remainder;
            return itemsHeight;
        };

        /**
         * Calculates total number of visible items to return a row height
         * @param {Number} rangeIndex The index to start refreshing range
         * @returns {Number} total Number of items visible (not in showrange but total).
         */
        this.calculateVisible = function _calculateVisible(rangeIndex) {
            rangeIndex = rangeIndex || 0;
            var len = self.flatData.length,
                total = 0,
                i,
                item;
            self.visibleIndexes = [];
            for (i = 0; i < len; i++) {
                item = Indexes[self.flatData[i].id];
                if (self.filterOn) {
                    if (self.rowFilterResult(item)) {
                        total++;
                        self.visibleIndexes.push(i);
                    }
                } else {
                    if (self.flatData[i].show) {
                        self.visibleIndexes.push(i);
                        total = total + 1;
                    }
                }
            }
            self.refreshRange(rangeIndex);
            return total;
        };

        /**
         * Refreshes the view to start the the location where begin is the starting index
         * @param {Number} begin The index location of visible indexes to start at.
         */
        this.refreshRange = function _refreshRange(begin, redraw) {
            redraw = redraw !== undefined ? redraw : true; // redraw by default
            var len = self.visibleIndexes.length,
                range = [],
                counter = 0,
                i,
                index;
            if (!begin || begin < 0 || begin > self.flatData.length) {
                begin = 0;
            }
            self.visibleTop = begin;
            for (i = begin; i < len; i++) {
                if (range.length === self.options.showTotal) {
                    break;
                }
                index = self.visibleIndexes[i];
                range.push(index);
                counter = counter + 1;
            }
            self.showRange = range;
            // TODO: Not sure if the redraw param is necessary. We can probably
            // Use m.start/endComputtion to avoid successive redraws
            if (redraw) {
                m.redraw(true);
            }
        };

        /**
         * Changes view to continous scroll when clicked on the scroll button
         */
        this.toggleScroll = function _toggleScroll() {
            self.options.paginate = false;
            self.select('.tb-paginate').removeClass('active');
            self.select('.tb-scroll').addClass('active');
            self.select('#tb-tbody').scrollTop((self.currentPage() - 1) * self.options.showTotal * self.options.rowHeight);
            self.calculateHeight();
        };

        /**
         * Changes view to pagination when clicked on the paginate button
         */
        this.togglePaginate = function _togglePaginate() {
            var firstIndex = self.showRange[0],
                first = self.visibleIndexes.indexOf(firstIndex),
                pagesBehind = Math.floor(first / self.options.showTotal),
                firstItem = (pagesBehind * self.options.showTotal);
            self.options.paginate = true;
            self.select('.tb-scroll').removeClass('active');
            self.select('.tb-paginate').addClass('active');
            self.currentPage(pagesBehind + 1);
            self.calculateHeight();
            self.refreshRange(firstItem);
        };

        /**
         * During pagination goes UP one page
         */
        this.pageUp = function _pageUp() {
            // get last shown item index and refresh view from that item onwards
            var lastIndex = self.showRange[self.options.showTotal - 1],
                last = self.visibleIndexes.indexOf(lastIndex);
            if (last > -1 && last + 1 < self.visibleIndexes.length) {
                self.refreshRange(last + 1);
                self.currentPage(self.currentPage() + 1);
                return true;
            }
            return false;
        };

        /**
         * During pagination goes DOWN one page
         */
        this.pageDown = function _pageDown() {
            var firstIndex = self.showRange[0],
                first = self.visibleIndexes.indexOf(firstIndex);
            if (first && first > 0) {
                self.refreshRange(first - self.options.showTotal);
                self.currentPage(self.currentPage() - 1);
                return true;
            }
            return false;
        };

        /**
         * During pagination jumps to specific page
         * @param {Number} value the page number to jump to
         */
        this.goToPage = function _goToPage(value) {
            if (value && value > 0 && value <= (Math.ceil(self.visibleIndexes.length / self.options.showTotal))) {
                var index = (self.options.showTotal * (value - 1));
                self.currentPage(value);
                self.refreshRange(index);
                return true;
            }
            return false;
        };

        /**
         * Check if item is part of the multiselected array
         * @param {Number} id The unique id of the item.
         * @returns {Boolean} outcome Whether the item is part of multiselected
         */
        this.isMultiselected = function (id) {
            var outcome = false;
            self.multiselected().map(function (item) {
                if (item.id === id) {
                    outcome = true;
                }
            });
            return outcome;
        };

        /**
         * Removes single item from the multiselected array
         * @param {Number} id The unique id of the item.
         * @returns {Boolean} result Whether the item removal was successful
         */
        this.removeMultiselected = function (id) {
            self.multiselected().map(function (item, index, arr) {
                if (item.id === id) {
                    arr.splice(index, 1);
                    // remove highlight
                    $('.tb-row[data-id="' + item.id + '"]').removeClass(self.options.hoverClassMultiselect);
                }
            });
            return false;
        };

        /**
         * Adds highlight to the multiselected items using jquery.
         */
        this.highlightMultiselect = function () {
            $('.' + self.options.hoverClassMultiselect).removeClass(self.options.hoverClassMultiselect);
            self.multiselected().map(function (item) {
                $('.tb-row[data-id="' + item.id + '"]').addClass(self.options.hoverClassMultiselect);
            });
        };

        /**
         * Handles multiselect by adding items through shift or control key presses
         * @param {Number} id The unique id of the item.
         * @param {Number} [index] The showRange index of the item
         * @param {Event} [event] Click event on the item
         */
        this.handleMultiselect = function (id, index, event) {
            var tree = Indexes[id],
                begin,
                end,
                i,
                cmdkey,
                direction;
            if (self.options.onbeforemultiselect) {
                self.options.onbeforemultiselect.call(self, event, tree);
            }
            // if key is shift
            if (self.pressedKey === 16) {
                // get the index of this and add all visible indexes between this one and last selected
                // If there is no multiselect yet
                if (self.multiselected().length === 0) {
                    self.multiselected().push(tree);
                } else {
                    begin = self.returnIndex(self.multiselected()[0].id);
                    end = self.returnIndex(id);
                    if (begin > end) {
                        direction = 'up';
                    } else {
                        direction = 'down';
                    }
                    if (begin !== end) {
                        self.multiselected([]);
                        if (direction === 'down') {
                            for (i = begin; i <= end; i++) {
                                self.multiselected().push(Indexes[self.flatData[i].id]);
                            }
                        }
                        if (direction === 'up') {
                            for (i = begin; i >= end; i--) {
                                self.multiselected().push(Indexes[self.flatData[i].id]);
                            }
                        }
                    }
                }
            }
            // if key is cmd
            cmdkey = 91; // works with mac
            if (window.navigator.userAgent.indexOf('MSIE') > -1 || window.navigator.userAgent.indexOf('Windows') > -1) {
                cmdkey = 17; // works with windows
            }
            if (window.navigator.userAgent.indexOf('Firefox') > -1) {
                cmdkey = 224; // works with Firefox
            }
            if (self.pressedKey === cmdkey) {
                if (!self.isMultiselected(tree.id)) {
                    self.multiselected().push(tree);
                } else {
                    self.removeMultiselected(tree.id);
                }
            }
            // if there is no key add the one.
            if (!self.pressedKey) {
                self.clearMultiselect();
                self.multiselected().push(tree);
            }

            if (self.options.onmultiselect) {
                self.options.onmultiselect.call(self, event, tree);
            }
            self.highlightMultiselect.call(this);
        };

        this.clearMultiselect = function () {
            $('.' + self.options.hoverClassMultiselect).removeClass(self.options.hoverClassMultiselect);
            self.multiselected([]);
        };

        // Handles the up and down arrow keys since they do almost identical work
        this.multiSelectArrows = function (direction){
            if ($.isFunction(self.options.onbeforeselectwitharrow)) {
                self.options.onbeforeselectwitharrow.call(this, self.multiselected()[0], direction);
            }
            var val = direction === 'down' ? 1 : -1;
            var selectedIndex = self.returnIndex(self.multiselected()[0].id);
            var visibleIndex = self.visibleIndexes.indexOf(selectedIndex);
            var newIndex = visibleIndex + val;
            var row = self.flatData[self.visibleIndexes[newIndex]];
            if(!row){
                return;
            }
            var treeItem = self.find(row.id);
            self.multiselected([treeItem]);
            self.scrollEdges(treeItem.id, 0);
            self.highlightMultiselect.call(self);
            if ($.isFunction(self.options.onafterselectwitharrow)) {
                self.options.onafterselectwitharrow.call(this, row, direction);
            }

        }

        // Handles the toggling of folders with the right and left arrow keypress
        this.keyboardFolderToggle = function (action) {
            var item = self.multiselected()[0];
            if(item.kind === 'folder') {
                if((item.open === true && action === 'close') || (item.open === false && action === 'open'))  {
                    var index = self.returnIndex(item.id);
                    self.toggleFolder(index, null);
                }
            }
        }

        // Handles what the up, down, left, right arrow keys do.
        this.handleArrowKeys = function (e) {
            if([32, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
                e.preventDefault();
            }
            var key = e.keyCode;
            // if pressed key is up arrow
            if(key === 38) {
                self.multiSelectArrows('up');
            }
            // if pressed key is down arrow
            if(key === 40) {
                self.multiSelectArrows('down');
            }
            // if pressed key is left arrow
            if(key === 37) {
                self.keyboardFolderToggle('close');
            }
            // if pressed key is right arrow
            if(key === 39) {
                self.keyboardFolderToggle('open');
            }
        }



        /**
         * Remove dropzone from grid
         */
        function _destroyDropzone() {
            self.dropzone.destroy();
        }

        /**
         * Apply dropzone to grid with the optional hooks
         */
        function _applyDropzone() {
            if (self.dropzone) {
                _destroyDropzone();
            } // Destroy existing dropzone setup

            var options = $.extend({
                clickable: false,
                counter: 0,
                accept: function _dropzoneAccept(file, done) {
                    var parent = file.treebeardParent;
                    if (self.options.addcheck.call(this, self, parent, file)) {
                        $.when(self.options.resolveUploadUrl.call(self, parent, file))
                            .then(function _resolveUploadUrlThen(newUrl) {
                                if (newUrl) {
                                    self.dropzone.options.url = newUrl;
                                    self.dropzone.options.counter++;
                                    if (self.dropzone.options.counter < 2) {
                                        var index = self.returnIndex(parent.id);
                                        if (!parent.open) {
                                            self.toggleFolder(index, null);
                                        }
                                    }
                                }
                                return newUrl;
                            })
                            .then(function _resolveUploadMethodThen() {
                                if ($.isFunction(self.options.resolveUploadMethod)) {
                                    self.dropzone.options.method = self.options.resolveUploadMethod.call(self, parent);
                                }
                            })
                            .done(function _resolveUploadUrlDone() {
                                done();
                            });
                    }
                },
                drop: function _dropzoneDrop(event, ui) {

                    var rowID = $(event.target).closest('.tb-row').attr('data-id');
                    var item = Indexes[rowID];
                    if (item.kind === 'file') {
                        item = item.parent();
                    }
                    self.dropzoneItemCache = item;
                    if (!item.open) {
                        var index = self.returnIndex(item.id);
                        self.toggleFolder(index, null);
                    }
                    if ($.isFunction(self.options.dropzoneEvents.drop)) {
                        self.options.dropzoneEvents.drop.call(this, self, event);
                    }

                },
                dragstart: function _dropzoneDragStart(event) {
                    if ($.isFunction(self.options.dropzoneEvents.dragstart)) {
                        self.options.dropzoneEvents.dragstart.call(this, self, event);
                    }
                },
                dragend: function _dropzoneDragEnd(event) {
                    if ($.isFunction(self.options.dropzoneEvents.dragend)) {
                        self.options.dropzoneEvents.dragend.call(this, self, event);
                    }
                },
                dragenter: function _dropzoneDragEnter(event) {
                    if ($.isFunction(self.options.dropzoneEvents.dragenter)) {
                        self.options.dropzoneEvents.dragenter.call(this, self, event);
                    }
                },
                dragover: function _dropzoneDragOver(event) {
                    if ($.isFunction(self.options.dropzoneEvents.dragover)) {
                        self.options.dropzoneEvents.dragover.call(this, self, event);
                    }
                },
                dragleave: function _dropzoneDragLeave(event) {
                    if ($.isFunction(self.options.dropzoneEvents.dragleave)) {
                        self.options.dropzoneEvents.dragleave.call(this, self, event);
                    }
                },
                success: function _dropzoneSuccess(file, response) {
                    if ($.isFunction(self.options.dropzoneEvents.success)) {
                        self.options.dropzoneEvents.success.call(this, self, file, response);
                    }
                    if ($.isFunction(self.options.onadd)) {
                        self.options.onadd.call(this, self, file.treebeardParent, file, response);
                    }
					filesSuccessArray.push(file.name)
                },
                error: function _dropzoneError(file, message, xhr) {
                    if ($.isFunction(self.options.dropzoneEvents.error)) {
                        self.options.dropzoneEvents.error.call(this, self, file, message, xhr);
                    }
					filesFailedArray.push(file.name)
                },
                uploadprogress: function _dropzoneUploadProgress(file, progress, bytesSent) {
                    if ($.isFunction(self.options.dropzoneEvents.uploadprogress)) {
                        self.options.dropzoneEvents.uploadprogress.call(this, self, file, progress, bytesSent);
                    }
                },
                sending: function _dropzoneSending(file, xhr, formData) {
                    var filesArr = this.getQueuedFiles();
                    if (filesArr.length  > 0) {
                        self.isUploading(true);
                    } else {
                        self.isUploading(false);
                    }
                    if ($.isFunction(self.options.dropzoneEvents.sending)) {
                        self.options.dropzoneEvents.sending.call(this, self, file, xhr, formData);
                    }
                },
                complete: function _dropzoneComplete(file) {
                    if ($.isFunction(self.options.dropzoneEvents.complete)) {
                        self.options.dropzoneEvents.complete.call(this, self, file);
                    }
					filesCompleteArray.push(file.name)
					if ( filesCompleteArray.length === filesDropArray.length ) {

						var filesSuccessList = [];
						var filesFailedList = [];

						for (var i = 0; i < filesSuccessArray.length; i++) {
							filesSuccessList.push( m('li', filesSuccessArray[i]) )
						}

						for (var i = 0; i < filesFailedArray.length; i++) {
							filesFailedList.push( m('li', filesFailedArray[i]) )
						}

						var mithrilUpload = [m('h3.break-word', 'Upload files')]

						if (filesSuccessArray.length > 0) {
							mithrilUpload.push([m('p', 'Success:'),
								m('ul', filesSuccessList)])
						}

						if (filesFailedArray.length > 0) {
							mithrilUpload.push([m('p', 'Failed:'),
								m('ul', filesFailedList)])
						}

						var mithrilContent = m('div', mithrilUpload);

						var mithrilButtons = m('div', [
							m('button', { 'class' : 'btn btn-success', onclick : function() { self.modal.dismiss(); } }, 'Ok'),
						]);
						self.modal.update(mithrilContent, mithrilButtons);

						filesDropArray.length = 0;
						filesCompleteArray.length = 0;
						filesFailedArray.length = 0;
						filesSuccessArray.length = 0;

						self.refreshData()

					}
                },
                queuecomplete: function _dropzoneComplete(file) {
                    self.isUploading(false);
                    if ($.isFunction(self.options.dropzoneEvents.queuecomplete)) {
                        self.options.dropzoneEvents.queuecomplete.call(this, self, file);
                    }
					console.log('eee')
                },
                addedfile: function _dropzoneAddedFile(file) {
                    file.treebeardParent = self.dropzoneItemCache;
                    if ($.isFunction(self.options.dropzoneEvents.addedfile)) {
                        self.options.dropzoneEvents.addedfile.call(this, self, file);
                    }
					filesDropArray.push(file.name)
                },
                removedfile: function _dropzoneRemovedFile(file) {
                    file.treebeardParent = self.dropzoneItemCache;
                    if ($.isFunction(self.options.dropzoneEvents.removedfile)) {
                        self.options.dropzoneEvents.removedfile.call(this, self, file);
                    }
                }
            }, self.options.dropzone); // Extend default options
            // Add Dropzone with different scenarios of library inclusion, should work for most installations
            var Dropzone;

            if (typeof module === 'object') {
                Dropzone = require('dropzone');
            } else {
                Dropzone = window.Dropzone;
            }


            if (typeof Dropzone === 'undefined') {
                throw new Error('To enable uploads Treebeard needs "Dropzone" to be installed.');
            }
            if (typeof Dropzone === 'undefined') {
              console.log('To enable uploads Treebeard needs "Dropzone" to be installed.');
            }
            // apply dropzone to the Treebeard object
            self.dropzone = new Dropzone('#' + self.options.divID, options); // Initialize dropzone
       }

        /**
         * Loads the data pushed in to Treebeard and handles it to comply with treebeard data structure.
         * @param {Array, String} data Data sent in as an array of objects or a url in string form
         */
        function _loadData(data) {
                // Order of operations: Gewt data -> build tree -> flatten for view -> calculations for view: visible, height
            if ($.isArray(data)) {
                $.when(self.buildTree(data)).then(function _buildTreeThen(value) {
                    self.treeData = value;
                    Indexes[self.treeData.id] = value;
                    self.flatten(self.treeData.children);
                    return value;
                }).done(function _buildTreeDone() {
                    self.calculateVisible();
                    self.calculateHeight();
                    self.initialized = true;
                    if ($.isFunction(self.options.ondataload)) {
                        self.options.ondataload.call(self);
                    }
                });
            } else {
                // then we assume it's a sring with a valiud url
                // I took out url validation because it does more harm than good here.
                m.request({
                    method: 'GET',
                    url: data,
                    config: self.options.xhrconfig,
                    extract: function (xhr, xhrOpts) {
                        var responseText = xhr.responseText;
                        try {
                            JSON.parse(responseText);
                        } catch (e) {
                            responseText = JSON.stringify(responseText);
                        }

                        if (xhr.status !== 200) {
                            self.options.ondataloaderror(xhr);
                        }

                        return responseText;
                    }
                })
                    .then(function _requestBuildtree(value) {
                        if (self.options.lazyLoadPreprocess) {
                            value = self.options.lazyLoadPreprocess.call(self, value);
                        }
                        self.treeData = self.buildTree(value);
                    })
                    .then(function _requestFlatten() {
                        Indexes[self.treeData.id] = self.treeData;
                        self.flatten(self.treeData.children);
                    })
                    .then(function _requestCalculate() {
                        self.calculateVisible();
                        self.calculateHeight();
                        self.initialized = true;
                        if ($.isFunction(self.options.ondataload)) {
                            self.options.ondataload.call(self);
                        }
                    });
            }
        }
            // Rebuilds the tree data with an API
        this.buildTree = function _buildTree(data, parent) {
            var tree, children, len, child, i;
            if (Array.isArray(data)) {
                tree = new Item();
                children = data;
            } else {
                tree = new Item(data);
                children = data.children;
                tree.depth = parent.depth + 1; // Going down the list the parent doesn't yet have depth information
            }
            if (children) {
                len = children.length;
                for (i = 0; i < len; i++) {
                    child = self.buildTree(children[i], tree);
                    tree.add(child);
                }
            }
            return tree;
        };

        /**
         * Turns the tree structure into a flat index of nodes
         * @param {Array} value Array of hierarchical objects
         * @param {Number} visibleTop Passes through the beginning point so that refreshes can work, default is 0.
         * @return {Array} value Returns a flat version of the hierarchical objects in an array.
         */
        this.flatten = function _flatten(value, visibleTop) {
            self.flatData = [];

            (function doFlatten(data, parentIsOpen) {
                $.each(data, function(index, item) {
                    Indexes[item.id] = item;

                    self.flatData.push({
                        show: parentIsOpen,

                        id: item.id,
                        row: item.data,
                        depth: item.depth,
                    });

                    if (item.children.length > 0) {
                        doFlatten(item.children, parentIsOpen && item.open);
                    }
                });
            })(value, true);

            self.calculateVisible(visibleTop);
            self.calculateHeight();
            m.redraw(true);
            if (self.options.redrawComplete) {
                self.options.redrawComplete.call(self);
            }

            return value;
        };

        /**
         * Update view on scrolling the table
         */
        this.onScroll = debounce(function _scrollHook() {
            var totalVisibleItems = self.visibleIndexes.length;
            if (!self.options.paginate) {
                if (totalVisibleItems > self.options.naturalScrollLimit) {
                    m.startComputation();
                    var $this = $(this);
                    var scrollTop, itemsHeight, innerHeight, location, index;
                    itemsHeight = self.calculateHeight();
                    innerHeight = $this.children('.tb-tbody-inner').outerHeight();
                    scrollTop = $this.scrollTop();
                    location = scrollTop / innerHeight * 100;
                    index = Math.floor(location / 100 * totalVisibleItems);
                    self.rangeMargin = index * self.options.rowHeight; // space the rows will have from the top.
                    self.refreshRange(index, false); // which actual rows to show
                    self.lastLocation = scrollTop;
                    self.highlightMultiselect();
                    m.endComputation();
                }
                if (self.options.onscrollcomplete) {
                    self.options.onscrollcomplete.call(self);
                }
            }
        }, this.options.scrollDebounce);

        /**
         * Initialization functions after the main body of the table is loaded
         * @param {Object} el The DOM element that config is run on
         * @param {Boolean} isInit Whether this function ran once after page load.
         */
        this.init = function _init(el, isInit) {
            var containerHeight = self.select('#tb-tbody').height(),
                titles = self.select('.tb-row-titles'),
                columns = self.select('.tb-th');
            if(self.options.naturalScrollLimit){
                self.options.showTotal = self.options.naturalScrollLimit;
            } else {
                self.options.showTotal = Math.floor(containerHeight / self.options.rowHeight) + 1;
            }

            self.remainder = (containerHeight / self.options.rowHeight) + self.options.rowHeight;
            // reapply move on view change.
            if (self.options.allowMove) {
                self.moveOn();
            }
            if (isInit) {
                return;
            }
            if (self.options.allowMove) {
                self.initializeMove(); // Needed to run once to establish drag and drop options
            }
            if (!self.options.rowHeight) { // If row height is not set get it from CSS
                self.options.rowHeight = self.select('.tb-row').height();
            }
            self.select('.gridWrapper').mouseleave(function() {
                self.select('.tb-row').removeClass(self.options.hoverClass);
            });
            // Main scrolling functionality
            self.select('#tb-tbody').scroll(self.onScroll);

            function _resizeCols() {
                var parentWidth = titles.width(),
                    percentageTotal = 0,
                    p;
                columns.each(function(index) { // calculate percentages for each column
                    var col = $(this),
                        lastWidth;
                    col.attr('data-tb-size', col.outerWidth());
                    if (index === self.select('.tb-th').length - 1) { // last column gets the remainder
                        lastWidth = 100 - percentageTotal;
                        self.colsizes[col.attr('data-tb-th-col')] = lastWidth;
                        col.css('width', lastWidth + '%');
                    } else {
                        p = col.outerWidth() / parentWidth * 100;
                        self.colsizes[col.attr('data-tb-th-col')] = p;
                        col.css('width', p + '%');
                    }
                    percentageTotal += p;
                });
            }

            function convertToPixels() {
                var parentWidth = titles.width(),
                    totalPixels = 0;
                columns.each(function (index) {
                    var col = $(this),
                        colWidth = parentWidth - totalPixels - 1,
                        width;
                    if (index === self.select('.tb-th').length - 1) { // last column gets the remainder
                        col.css('width', colWidth + 'px'); // -1 for the border
                    } else {
                        width = col.outerWidth();
                        col.css('width', width);
                        totalPixels += width;
                    }
                });
            }
            self.select('.tb-th.tb-resizable').resizable({
                containment: 'parent',
                delay: 200,
                handles: 'e',
                minWidth: 60,
                start: function (event, ui) {
                    convertToPixels();
                },
                create: function (event, ui) {
                    // change cursor
                    self.select('.ui-resizable-e').css({
                        "cursor": "col-resize"
                    });
                },
                resize: function (event, ui) {
                    var thisCol = $(this),
                        index = $(this).attr('data-tb-th-col'),
                        totalColumns = columns.length,
                        // if the overall size is getting bigger than home size, make other items smaller
                        parentWidth = titles.width() - 1,
                        childrenWidth = 0,
                        diff,
                        nextBigThing,
                        nextBigThingIndex,
                        lastBigThing,
                        lastBigThingIndex,
                        diff2,
                        diff3,
                        w2,
                        w3,
                        lastWidth,
                        colWidth;
                    columns.each(function() {
                        childrenWidth = childrenWidth + $(this).outerWidth();
                    });
                    if (childrenWidth > parentWidth) {
                        diff2 = childrenWidth - parentWidth;
                        nextBigThing = columns.not(ui.element).filter(function() {
                            var colElement = parseInt($(ui.element).attr('data-tb-th-col')),
                                colThis = parseInt($(this).attr('data-tb-th-col'));
                            if (colThis > colElement) {
                                return $(this).outerWidth() > 40;
                            }
                            return false;
                        }).first();
                        if (nextBigThing.length > 0) {
                            w2 = nextBigThing.outerWidth();
                            nextBigThing.css({
                                width: (w2 - diff2) + 'px'
                            });
                            nextBigThingIndex = nextBigThing.attr('data-tb-th-col');
                            self.select('.tb-col-' + nextBigThingIndex).css({
                                width: (w2 - diff2) + 'px'
                            });
                        } else {
                            $(ui.element).css({
                                width: $(ui.element).attr('data-tb-currentSize') + 'px'
                            });
                            return;
                        }
                    }
                    if (childrenWidth < parentWidth) {
                        diff3 = parentWidth - childrenWidth;
                        // number of children other than the current element with widths bigger than 40
                        lastBigThing = columns.not(ui.element).filter(function() {
                            var $this = $(this);
                            return $this.outerWidth() < parseInt($this.attr('data-tb-size'));
                        }).last();
                        if (lastBigThing.length > 0) {
                            w3 = lastBigThing.outerWidth();
                            lastBigThing.css({
                                width: (w3 + diff3) + 'px'
                            });
                            lastBigThingIndex = lastBigThing.attr('data-tb-th-col');
                            self.select('.tb-col-' + lastBigThingIndex).css({
                                width: (w3 + diff3) + 'px'
                            });
                        } else {
                            w3 = columns.last().outerWidth();
                            columns.last().css({
                                width: (w3 + diff3) + 'px'
                            }).attr('data-tb-size', w3 + diff3);
                        }
                    }
                    // make the last column rows be same size as last column header
                    lastWidth = columns.last().width();
                    self.select('.tb-col-' + (totalColumns - 1)).css('width', lastWidth + 'px');

                    $(ui.element).attr('data-tb-currentSize', $(ui.element).outerWidth());
                    // change corresponding columns in the table
                    colWidth = thisCol.outerWidth();
                    self.select('.tb-col-' + index).css({
                        width: colWidth + 'px'
                    });
                },
                stop: function (event, ui) {
                    _resizeCols();
                    m.redraw(true);
                }
            });
            if (self.options.uploads) {
                _applyDropzone();
            }
            if ($.isFunction(self.options.onload)) {
                self.options.onload.call(self);
            }
            $(window).on('keydown', function(event){
                if(self.options.allowArrows && self.multiselected().length === 1) {
                    self.handleArrowKeys(event);
                }
            });
            if (self.options.multiselect) {
                $(window).keydown(function (event) {
                    self.pressedKey = event.keyCode;
                });
                $(window).keyup(function (event) {
                    self.pressedKey = undefined;
                });
            }
            $(window).keydown(function (event) {
                // if escape cancel modal - 27
                if (self.modal.on && event.keyCode === 27) {
                    self.modal.dismiss();
                }
                // if enter then run the modal - 13
                if (self.modal.on && event.keyCode === 13) {
                    self.select('.tb-modal-footer .btn-success').trigger('click');
                }
            });
            window.onblur = self.resetKeyPress;

            $(window).resize(function () {
                self.setScrollMode();
            });
            self.setScrollMode();
        };

        this.setScrollMode = function _setScrollMode() {
            if(self.options.hScroll && $('#' + self.options.divID).width() < self.options.hScroll){
                self.tableWidth(self.options.hScroll + 'px;');
            } else {
                self.tableWidth('auto;');
            }
        }
        /**
         * Resets keys that are hung up. Other window onblur event actions can be added in here.
         */
        this.resetKeyPress = function() {
                self.pressedKey = undefined;
            };
            /**
             * Destroys Treebeard by emptying the DOM object and removing dropzone
             * Because DOM objects are removed their events are going to be cleaned up.
             */
        this.destroy = function _destroy() {
            var el = document.getElementById(self.options.divID);
            var parent = el.parentNode;
            var clone = el.cloneNode(true);
            while (clone.firstChild) {
                clone.removeChild(clone.firstChild);
            }
            parent.removeChild(el);
            parent.appendChild(clone);
            if (self.dropzone) {
                _destroyDropzone();
            } // Destroy existing dropzone setup
        };

        /**
         * Checks if there is filesData option, fails if there isn't, initiates the entire app if it does.
         */
        if (self.options.filesData) {
            _loadData(self.options.filesData);
        } else {
            throw new Error("Treebeard Error: You need to define a data source through 'options.filesData'");
        }
    };

    /**
     * Mithril View. Documentation is here: (http://lhorie.github.io/mithril/mithril.html) Use m() for templating.
     * @param {Object} ctrl The entire Treebeard.controller object with its values and methods. Refer to as ctrl.
     */
    Treebeard.view = function treebeardView(ctrl) {
        return m('.gridWrapper', [ //, { style : 'overflow-x: auto' }
                m(".tb-table", { style : 'width:' + ctrl.tableWidth() }, [
                    /**
                     * Template for the head row, includes whether filter or title should be shown.
                     */
                    (function showHeadA() {
                        if(ctrl.options.toolbarComponent) {
                            return m.component(ctrl.options.toolbarComponent, {treebeard : ctrl, mode : null });
                        }
                        return ctrl.options.headerTemplate.call(ctrl);
                    }()), (function () {
                        if (!ctrl.options.hideColumnTitles) {
                            return m(".tb-row-titles", [
                                /**
                                 * Render column titles based on the columnTitles option.
                                 */

                                ctrl.options.columnTitles.call(ctrl).map(function _mapColumnTitles(col, index, arr) {
                                    var sortView = "",
                                        up,
                                        down,
                                        resizable = '.tb-resizable';
                                    var width = ctrl.colsizes[index] ? ctrl.colsizes[index] + '%' : col.width;
                                    if (!ctrl.options.resizeColumns) { // Check if columns can be resized.
                                        resizable = '';
                                    }
                                    if (index === arr.length - 1) { // Last column itself is not resizable because you don't need to
                                        resizable = '';
                                    }
                                    if (col.sort) { // Add sort buttons with their onclick functions
                                        if(!ctrl.isSorted[index]) {
                                            ctrl.isSorted[index] = {
                                                asc: false,
                                                desc: false
                                            }
                                        };
                                        if (ctrl.options.sortButtonSelector.up) {
                                            up = ctrl.options.sortButtonSelector.up;
                                        } else {
                                            up = 'i.fa.fa-sort-asc';
                                        }

                                        if (ctrl.options.sortButtonSelector.down) {
                                            down = ctrl.options.sortButtonSelector.down;
                                        } else {
                                            down = 'i.fa.fa-sort-desc';
                                        }
                                        sortView = [
                                            m(up + '.tb-sort-inactive.asc-btn.m-r-xs', {
                                                onclick: ctrl.sortToggle.bind(index),
                                                "data-direction": "asc",
                                                "data-sortType": col.sortType
                                            }),
                                            m(down + '.tb-sort-inactive.desc-btn', {
                                                onclick: ctrl.sortToggle.bind(index),
                                                "data-direction": "desc",
                                                "data-sortType": col.sortType
                                            })
                                        ];
                                    }
                                    return m('.tb-th' + resizable, {
                                        style: "width: " + width,
                                        'data-tb-th-col': index
                                    }, [
                                        m('span.m-r-sm', col.title),
                                        sortView
                                    ]);
                                })

                            ]);
                        }
                    }()),
                    m("#tb-tbody", {
                        config: ctrl.init
                    }, [
                        /**
                         * In case a modal needs to be shown, check Modal object
                         */
                        (function showModal() {
                            var dissmissTemplate = m('button.close', {
                                            'onclick': function() {
                                                ctrl.modal.dismiss();
                                            }
                                        }, [ctrl.options.removeIcon()]);
                            if (ctrl.modal.on) {
                                return m('.tb-modal-shade', {
                                    config: ctrl.modal.onmodalshow,
                                    style: 'width:' + ctrl.modal.width + 'px; height:' + ctrl.modal.height + 'px;padding:' + ctrl.modal.padding,
                                    onclick : function(event) {
                                        ctrl.modal.dismiss();
                                    }
                                }, [
                                    m('.modal-content', {
                                        'class': ctrl.modal.css,
                                        onclick : function(event) {
                                            event.stopPropagation();
                                            return true;
                                        }
                                    }, [
                                        (function checkHeader(){
                                            if(ctrl.modal.header){
                                                return [ m('.modal-header', [
                                                    dissmissTemplate,
                                                    ctrl.modal.header
                                                    ]),
                                                 m('.modal-body', ctrl.modal.content)
                                                ];
                                            } else {
                                                return [
                                                m('.modal-body', [
                                                    dissmissTemplate,
                                                    ctrl.modal.content
                                                    ])
                                                ];
                                            }
                                        }()),
                                        m('.modal-footer', ctrl.modal.actions)
                                    ])
                                ]);
                            }
                        }()),
                        m('.tb-tbody-inner', {
                            style: 'height: ' + ctrl.innerHeight + 'px;'

                        }, [
                            m('', {
                                style: "margin-top:" + ctrl.rangeMargin + 'px;'
                            }, [
                                /**
                                 * showRange has the several items that get shown at a time. It's key to view optimization
                                 * showRange values change with scroll, filter, folder toggling etc.
                                 */
                                ctrl.showRange.length === 0 && ctrl.filterOn ?
                                    m('.tb-no-results', 'No results found for this search term.')
                                    : ctrl.showRange.map(function _mapRangeView(item, index) {
                                    var oddEvenClass = ctrl.options.oddEvenClass.odd,
                                        indent = ctrl.flatData[item].depth,
                                        id = ctrl.flatData[item].id,
                                        tree = Indexes[id],
                                        row = ctrl.flatData[item].row,
                                        padding,
                                        css = tree.css || "",
                                        rowCols = ctrl.options.resolveRows.call(ctrl, tree);
                                    if (index % 2 === 0) {
                                        oddEvenClass = ctrl.options.oddEvenClass.even;
                                    }
                                    if (ctrl.filterOn) {
                                        padding = 20;
                                    } else {
                                        padding = (indent - 1) * 20;
                                    }
                                    if (tree.notify.on && !tree.notify.column) { // In case a notification is taking up the column space
                                        return m('.tb-row',{'style': "height: " + ctrl.options.rowHeight + "px;"}, [
                                            m('.tb-notify.alert-' + tree.notify.type, {
                                                'class': tree.notify.css
                                            }, [
                                                m('span', tree.notify.message)
                                            ])
                                        ]);
                                    } else {
                                        return m(".tb-row", { // Events and attribtues for entire row
                                            "key": id,
                                            "class": css + " " + oddEvenClass,
                                            "data-id": id,
                                            "data-level": indent,
                                            "data-index": item,
                                            "data-rIndex": index,
                                            style: "height: " + ctrl.options.rowHeight + "px;",
                                            onclick: function _rowClick(event) {
                                                var el = $(event.target);
                                                if(el.hasClass('tb-toggle-icon') || el.hasClass('fa-plus') || el.hasClass('fa-minus')) {
                                                    return;
                                                }
                                                if (ctrl.options.multiselect) {
                                                    ctrl.handleMultiselect(id, index, event);
                                                }
                                                ctrl.selected = id;
                                                if (ctrl.options.onselectrow) {
                                                    ctrl.options.onselectrow.call(ctrl, tree, event);
                                                }
                                            },
                                            ondblclick : function _ondblclick(event){
                                                var self = this;
                                                if ($.isFunction(ctrl.options.ondblclickrow)) {
                                                    ctrl.options.ondblclickrow.call(ctrl, tree, event);
                                                }
                                            },
                                            onmouseover: function _rowMouseover(event) {
                                                ctrl.mouseon = id;
                                                if (ctrl.options.hoverClass && !ctrl.dragOngoing) {
                                                    ctrl.select('.tb-row').removeClass(ctrl.options.hoverClass);
                                                    $(this).addClass(ctrl.options.hoverClass);
                                                }
                                                if (ctrl.options.onmouseoverrow) {
                                                    ctrl.options.onmouseoverrow.call(ctrl, tree, event);
                                                }
                                            }
                                        }, [
                                            /**
                                             * Build individual columns depending on the resolveRows
                                             */
                                            rowCols.map(function _mapColumnsContent(col, index) {
                                                var cell,
                                                    title,
                                                    colInfo = ctrl.options.columnTitles.call(ctrl)[index],
                                                    colcss = col.css || '';
                                                var width = ctrl.colsizes[index] ? ctrl.colsizes[index] + '%' : colInfo.width;
                                                cell = m('.tb-td.tb-col-' + index, {
                                                    'class': colcss,
                                                    style: "width:" + width
                                                }, [
                                                    m('span', row[col.data])
                                                ]);
                                                if (tree.notify.on && tree.notify.column === index) {
                                                    return m('.tb-td.tb-col-' + index, {
                                                        style: "width:" + width
                                                    }, [
                                                        m('.tb-notify.alert-' + tree.notify.type, {
                                                            'class': tree.notify.css
                                                        }, [
                                                            m('span', tree.notify.message)
                                                        ])
                                                    ]);
                                                }
                                                if (col.folderIcons) {
                                                    if (col.custom) {
                                                        title = m("span.title-text", col.custom.call(ctrl, tree, col));
                                                    } else {
                                                        title = m("span.title-text", row[col.data] + " ");
                                                    }
                                                    cell = m('.tb-td.td-title.tb-col-' + index, {
                                                        "data-id": id,
                                                        'class': colcss,
                                                        style: "padding-left: " + padding + "px; width:" + width
                                                    }, [
                                                        m("span.tb-td-first", // Where toggling and folder icons are
                                                            (function _toggleView() {
                                                                var resolveIcon = ctrl.options.resolveIcon.call(ctrl, tree); // Should return false if no icon is needed
                                                                var resolveToggle = ctrl.options.resolveToggle.call(ctrl, tree); // Should return false if no icon is needed
                                                                var set = [{
                                                                    'id': 1,
                                                                    'css': 'tb-expand-icon-holder',
                                                                    'resolve': resolveIcon
                                                                }, {
                                                                    'id': 2,
                                                                    'css': 'tb-toggle-icon',
                                                                    'resolve': resolveToggle
                                                                }];
                                                                var templateIcon = m('span.' + set[0].css, {
                                                                        key: set[0].id
                                                                    },
                                                                    set[0].resolve
                                                                );
                                                                var templateToggle = m('span.' + set[1].css, {
                                                                    key: set[1].id,
                                                                    onclick: function _folderToggleClick(event) {
                                                                        if (ctrl.options.togglecheck.call(ctrl, tree)) {
                                                                            ctrl.toggleFolder(item, event);
                                                                        }
                                                                    }
                                                                }, set[1].resolve);
                                                                if (ctrl.filterOn && resolveIcon) {
                                                                    return templateIcon;
                                                                }
                                                                return [
                                                                    templateToggle, // Don't make toggle optional
                                                                    resolveIcon ? templateIcon : ''
                                                                ];
                                                            }())
                                                        ),
                                                        title
                                                    ]);
                                                }
                                                if (!col.folderIcons && col.custom) { // If there is a custom call.
                                                    cell = m('.tb-td.tb-col-' + index, {
                                                        'class': colcss,
                                                        style: "width:" + width
                                                    }, [
                                                        col.custom.call(ctrl, tree, col)
                                                    ]);
                                                }
                                                return cell;
                                            })
                                        ]);
                                    }

                                })
                            ])

                        ])
                    ]),
                    /**
                     * Footer, scroll/paginate toggle, page numbers.
                     */
                    (function _footer() {
                        if (ctrl.options.paginate || ctrl.options.paginateToggle) {
                            return m('.tb-footer', [
                                m(".row", [
                                    m(".col-xs-4", (function _showPaginateToggle() {
                                        if (ctrl.options.paginateToggle) {
                                            var activeScroll = "",
                                                activePaginate = "";
                                            if (ctrl.options.paginate) {
                                                activePaginate = "active";
                                            } else {
                                                activeScroll = "active";
                                            }
                                            return m('.btn-group.padder-10', [
                                                m("button.tb-button.tb-scroll", {
                                                        onclick: ctrl.toggleScroll,
                                                        "class": activeScroll
                                                    },
                                                    "Scroll"),
                                                m("button.tb-button.tb-paginate", {
                                                        onclick: ctrl.togglePaginate,
                                                        "class": activePaginate
                                                    },
                                                    "Paginate")
                                            ]);
                                        }
                                    }())),
                                    m('.col-xs-8', [m('.padder-10', [
                                        (function _showPaginate() {
                                            if (ctrl.options.paginate) {
                                                var total_visible = ctrl.visibleIndexes.length,
                                                    total = Math.ceil(total_visible / ctrl.options.showTotal);
                                                if (ctrl.options.resolvePagination) {
                                                    return ctrl.options.resolvePagination.call(ctrl, total, ctrl.currentPage());
                                                }
                                                return m('.tb-pagination.pull-right', [
                                                    m('button.tb-pagination-prev.tb-button.m-r-sm', {
                                                        onclick: ctrl.pageDown
                                                    }, [m('i.fa.fa-chevron-left')]),
                                                    m('input.tb-pagination-input.m-r-sm', {
                                                        type: "text",
                                                        style: "width: 30px;",
                                                        onkeyup: function(e) {
                                                            var page = parseInt(e.target.value, 10);
                                                            ctrl.goToPage(page);
                                                        },
                                                        value: ctrl.currentPage()
                                                    }),
                                                    m('span.tb-pagination-span', "/ " + total + " "),
                                                    m('button.tb-pagination-next.tb-button', {
                                                        onclick: ctrl.pageUp
                                                    }, [m('i.fa.fa-chevron-right')])
                                                ]);
                                            }
                                        }())
                                    ])])
                                ])
                            ]);
                        }
                    }())
                ])
            ])
    };

    /**
     * Treebeard default options as a constructor so multiple different types of options can be established.
     * Implementations have to declare their own "filesData", "columnTitles", "resolveRows", all others are optional
     */
    var Options = function() {
        this.divID = "myGrid"; // This div must be in the html already or added as an option
        this.filesData = "small.json"; // REQUIRED: Data in Array or string url
        this.rowHeight = undefined; // user can override or get from .tb-row height
        this.paginate = false; // Whether the applet starts with pagination or not.
        this.paginateToggle = false; // Show the buttons that allow users to switch between scroll and paginate.
        this.uploads = false; // Turns dropzone on/off.
        this.multiselect = false; // turns ability to multiselect with shift or command keys
        this.naturalScrollLimit = 50; // If items to show is below this number, onscroll should not be run.
        this.columnTitles = function() { // REQUIRED: Adjust this array based on data needs.
            return [{
                title: "Title",
                width: "50%",
                sortType: "text",
                sort: true
            }, {
                title: "Author",
                width: "25%",
                sortType: "text"
            }, {
                title: "Age",
                width: "10%",
                sortType: "number"
            }, {
                title: "Actions",
                width: "15%"
            }];
        };
        this.hideColumnTitles = false;
        this.resolveRows = function(item) { // REQUIRED: How rows should be displayed based on data.
            return [{
                data: "title", // Data field name
                folderIcons: true,
                filter: true
            }];
        };
        this.hScroll  = 400; // Number which is the cut off for horizontal scrolling, can also be null;
        this.filterPlaceholder = 'Search';
        this.resizeColumns = true; // whether the table columns can be resized.
        this.hoverClass = undefined; // Css class for hovering over rows
        this.hoverClassMultiselect = 'tb-multiselect'; // Css class for hover on multiselect
        this.showFilter = true; // Gives the option to filter by showing the filter box.
        this.title = null; // Title of the grid, boolean, string OR function that returns a string.
        this.allowMove = true; // Turn moving on or off.
        this.allowArrows = false;
        this.moveClass = undefined; // Css class for which elements can be moved. Your login needs to add these to appropriate elements.
        this.sortButtonSelector = {}; // custom buttons for sort, needed because not everyone uses FontAwesome
        this.dragOptions = {}; // jQuery UI draggable options without the methods
        this.dropOptions = {}; // jQuery UI droppable options without the methods
        this.dragEvents = {}; // users can override draggable options and events
        this.dropEvents = {}; // users can override droppable options and events
        this.dragContainment = '.tb-tbody-inner';
        this.sortDepth = 0;
        this.oddEvenClass = {
            odd: 'tb-odd',
            even: 'tb-even'
        };
        this.onload = function() {
            // this = treebeard object;
        };
        this.togglecheck = function(item) {
            // this = treebeard object;
            // item = folder to toggle
            return true;
        };
        this.filterTemplate = function () {
            var tb = this;
            return m("input.pull-right.form-control.tb-input[placeholder='" + tb.options.filterPlaceholder + "'][type='text']", {
                style: "width:100%;display:inline;",
                onkeyup: tb.filter,
                value: tb.filterText()
            });
        };
        this.toolbarComponent = null;
        this.headerTemplate = function () {
            var ctrl = this;
            var titleContent = functionOrString(ctrl.options.title);

            if (ctrl.options.showFilter || titleContent) {
                var title = m('.tb-head-title', {}, titleContent);

                var filter = m(".tb-head-filter", {}, [
                    (function showFilterA() {
                        if (ctrl.options.showFilter) {
                            return ctrl.options.filterTemplate.call(ctrl);
                        }
                    }())
                ]);
                if (ctrl.options.title) {
                    return m('.tb-head', [
                        title,
                        filter

                    ]);
                } else {
                    return m('.tb-head', [
                        filter
                    ]);
                }

            }
        }
        this.onfilter = function(filterText) { // Fires on keyup when filter text is changed.
            // this = treebeard object;
            // filterText = the value of the filtertext input box.
        };
        this.onfilterreset = function(filterText) { // Fires when filter text is cleared.
            // this = treebeard object;
            // filterText = the value of the filtertext input box.
        };
        this.createcheck = function(item, parent) {
            // this = treebeard object;
            // item = Item to be added.  raw item, not _item object
            // parent = parent to be added to = _item object
            return true;
        };
        this.oncreate = function(item, parent) { // When new row is added
            // this = treebeard object;
            // item = Item to be added.  = _item object
            // parent = parent to be added to = _item object
        };
        this.deletecheck = function(item) { // When user attempts to delete a row, allows for checking permissions etc.
            // this = treebeard object;
            // item = Item to be deleted.
            return true;
        };
        this.ondelete = function() { // When row is deleted successfully
            // this = treebeard object;
            // item = a shallow copy of the item deleted, not a reference to the actual item
        };
        this.addcheck = function(treebeard, item, file) { // check is a file can be added to this item
            // this = dropzone object
            // treebeard = treebeard object
            // item = item to be added to
            // file = info about the file being added
            return true;
        };
        this.onadd = function(treebeard, item, file, response) {
            // this = dropzone object;
            // item = item the file was added to
            // file = file that was added
            // response = what's returned from the server
        };
        this.onselectrow = function(row, event) {
            // this = treebeard object
            // row = item selected
            // event = mouse click event object
        };
        this.ondblclickrow = function(row, event) {
            // this = treebeard object
            // row = item selected
            // event = mouse click event object
        };
        this.onbeforemultiselect = function(event, tree) {
            // this = treebeard object
            // tree = item currently clicked on
            // event = mouse click event object
        };
        this.onmultiselect = function(event, tree) {
            // this = treebeard object
            // tree = item currently clicked on
            // event = mouse click event object
        };
        this.onmouseoverrow = function(row, event) {
            // this = treebeard object
            // row = item selected
            // event = mouse click event object
        };
        this.ontogglefolder = function(item) {
            // this = treebeard object
            // item = toggled folder item
        };
        this.dropzone = { // All dropzone options.
            url: null // When users provide single URL for all uploads
        };
        this.dropzoneEvents = {};
        this.resolveIcon = function(item) { // Here the user can interject and add their own icons, uses m()
            // this = treebeard object;
            // Item = item acted on
            if (item.kind === "folder") {
                if (item.open) {

                    return m("i.fa.fa-folder-open-o", " ");
                }
                return m("i.fa.fa-folder-o", " ");
            }
            if (item.data.icon) {
                return m("i.fa." + item.data.icon, " ");
            }
            return m("i.fa.fa-file ");
        };
        this.removeIcon = function(){
            return m('i.fa.fa-remove');
        },
        this.resolveRefreshIcon = function() {
            return m('i.icon-refresh.icon-spin');
        };
        this.resolveToggle = function(item) {
            var toggleMinus = m("i.fa.fa-minus-square-o", " "),
                togglePlus = m("i.fa.fa-plus-square-o", " ");
            if (item.kind === "folder") {
                if (item.children.length > 0) {
                    if (item.open) {
                        return toggleMinus;
                    }
                    return togglePlus;
                }
            }
            return "";
        };
        this.resolvePagination = function(totalPages, currentPage) {
            // this = treebeard object
            return m("span", [
                m('span', 'Page: '),
                m('span.tb-pageCount', currentPage),
                m('span', ' / ' + totalPages)
            ]);
        };
        this.resolveUploadUrl = function(item) { // Allows the user to calculate the url of each individual row
            // this = treebeard object;
            // Item = item acted on return item.data.ursl.upload
            return "/upload";
        };
        this.resolveLazyloadUrl = function(item) {
            // this = treebeard object;
            // Item = item acted on
            return false;
        };
        this.lazyLoadError = function(item) {
            // this = treebeard object;
            // Item = item acted on
        };
        this.lazyLoadOnLoad = function(item) {
            // this = treebeard object;
            // Item = item acted on
        };
        this.ondataload = function(item) {
            // this = treebeard object;
        };
        this.ondataloaderror = function(xhr){
            // xhr with non-200 status code
        };
        this.onbeforeselectwitharrow = function(item, direction){
            // this = treebeard object;
            // Item = item where selection is going to
            // direction =  the directino of the arrow key
        };
        this.onafterselectwitharrow = function(item, direction){
            // this = treebeard object;
            // Item = item where selection is coming from
            // direction = the directino of the arrow key
        };
        this.xhrconfig = function(xhr, options){
            // xhr = xml http request
            // options = xhr options
        };
        this.scrollDebounce = 15; // milliseconds
    };

    /**
     * Starts treebard with user options
     * This may seem convoluted but is useful to encapsulate Treebeard instances.
     * @param {Object} options The options user passes in; will be expanded with defaults.
     * @returns {*}
     */
    var runTB = function _treebeardRun(options, component) {
        var defaults = new Options();
        var finalOptions = $.extend(defaults, options);
        // Weird fix for IE 9, does not harm regular load
        if (window.navigator.userAgent.indexOf('MSIE') !== -1) {
            setTimeout(function() {
                m.redraw();
            }, 1000);
        }
        if(!component){ // If not added as component into mithril view then mount it
            return m.mount(document.getElementById(finalOptions.divID), m.component(Treebeard, finalOptions));
        }
        return m.component(Treebeard, finalOptions); // Return component instead
    };


    // Expose some internal classes to the public
    runTB.Notify = Notify;

    return runTB;
}));
