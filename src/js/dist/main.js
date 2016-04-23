"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

exports.default = function () {
    var _this = this;

    var id = function id(x) {
        return x;
    };
    return {
        body: document.body,
        weekDays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        models: {
            Podcast: [["id", parseInt], ["title", id], ["feed_url", id], ["homepage", id], ["language", id], ["episode_count", parseInt], ["explicit", Boolean], ["summary", id]],
            Episode: [["id", parseInt], ["date", id], ["title", id], ["podcast_id", parseInt], ["week_day", function (wd) {
                return _this.weekDays[wd];
            }], ["day_of_month", id]],
            Category: [["id", parseInt], ["name", id]],
            User: [["id", parseInt], ["name", id], ["email", id], ["public", Boolean]]
        },
        makeTable: function makeTable(_ref) {
            var model = _ref.model;
            var result = _ref.result;

            var displayModel = this.models[model];
            var table = document.createElement('<table>');
            var header = this.makeHeader(displayModel);
            var content = this.makeContent(displayModel, data);
            document.appendChild(table, header);
            document.appendChild(table, content);
            document.appendChild(this.body, table);
        },
        makeHeader: function makeHeader(displayModel) {
            var col = void 0;
            var thead = document.createElement('<thead>');
            var tr = document.createElement('<tr>');
            var _iteratorNormalCompletion = true;
            var _didIteratorError = false;
            var _iteratorError = undefined;

            try {
                for (var _iterator = displayModel[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                    col = _step.value;

                    var th = document.createElement('<th>');
                    th.textContent = col[0];
                    document.appendChild(tr, th);
                }
            } catch (err) {
                _didIteratorError = true;
                _iteratorError = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion && _iterator.return) {
                        _iterator.return();
                    }
                } finally {
                    if (_didIteratorError) {
                        throw _iteratorError;
                    }
                }
            }

            document.appendChild(tr, thead);
            return thead;
        },
        makeContent: function makeContent(displayModel, data) {
            var row = void 0,
                key = void 0,
                val = void 0;
            var tbody = document.createElement('<tbody>');
            var _iteratorNormalCompletion2 = true;
            var _didIteratorError2 = false;
            var _iteratorError2 = undefined;

            try {
                for (var _iterator2 = data[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                    row = _step2.value;

                    var tr = document.createElement('<tr>');
                    var _iteratorNormalCompletion3 = true;
                    var _didIteratorError3 = false;
                    var _iteratorError3 = undefined;

                    try {
                        for (var _iterator3 = displayModel[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
                            var _step3$value = _slicedToArray(_step3.value, 2);

                            label = _step3$value[0];
                            fn = _step3$value[1];

                            var td = document.createElement('<td>');
                            td.textContent = fn(row[label]);
                            document.appendChild(tr, td);
                        }
                    } catch (err) {
                        _didIteratorError3 = true;
                        _iteratorError3 = err;
                    } finally {
                        try {
                            if (!_iteratorNormalCompletion3 && _iterator3.return) {
                                _iterator3.return();
                            }
                        } finally {
                            if (_didIteratorError3) {
                                throw _iteratorError3;
                            }
                        }
                    }

                    ;
                    document.appendChild(tbody, tr);
                }
            } catch (err) {
                _didIteratorError2 = true;
                _iteratorError2 = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion2 && _iterator2.return) {
                        _iterator2.return();
                    }
                } finally {
                    if (_didIteratorError2) {
                        throw _iteratorError2;
                    }
                }
            }

            return tbody;
        },
        attach: function attach(target) {
            Object.assign(target, { makeTable: this.makeTable });
        }
    };
};
'use strict';

var _retriever = require('retriever');

var _retriever2 = _interopRequireDefault(_retriever);

var _dom = require('dom');

var _dom2 = _interopRequireDefault(_dom);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var init = function init() {
    (0, _retriever2.default)().attach(document.window);
    (0, _dom2.default)().attach(document.window);
};
init();
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});

exports.default = function () {
    return {
        getResource: function getResource(model) {
            var _this = this;

            var method = arguments.length <= 1 || arguments[1] === undefined ? "GET" : arguments[1];

            var ep = void 0;
            if (ep = this.endpoints[model][method], ep !== undefined) {
                return function () {
                    return { url: "" + _this.homepage + ep.apply(undefined, arguments), method: method };
                };
            }
        },
        retrieve: function retrieve(_ref) {
            var url = _ref.url;
            var method = _ref.method;

            return new Promise(function (resolve, reject) {
                var req = new XMLHttpRequest();
                req.open(method, url);
                req.onload = function () {
                    if (req.status == 200) {
                        resolve(JSON.parse(req.responseText));
                    } else {
                        reject(Error(req.status, JSON.parse(req.responseText)));
                    }
                };
                req.onerror = function () {
                    reject(Error(-1));
                };
                req.send();
            });
        },
        attach: function attach(target) {
            Object.assign(target, { getResource: this.getResource, retrieve: this.retrieve });
        },

        homepage: "http://localhost:8000",
        endpoints: {
            categories: {
                GET: {
                    endpoint: function endpoint(category_id) {
                        return "/categories/" + category_id;
                    }
                }
            },
            podcasts: {
                GET: {
                    endpoint: function endpoint(podcast_id) {
                        return "/podcasts/" + podcast_id;
                    }
                }
            },
            likers: {
                GET: {
                    endpoint: function endpoint(podcast_id) {
                        return "/podcasts/" + podcast_id + "/likers";
                    }
                }
            },
            dislikers: {
                GET: {
                    endpoint: function endpoint(podcast_id) {
                        return "/podcasts/" + podcast_id + "/dislikers";
                    }
                }
            },
            podcast_categories: {
                GET: {
                    endpoint: function endpoint(podcast_id) {
                        return "/podcasts/" + podcast_id + "/categories";
                    }
                }
            },
            users: {
                GET: {
                    endpoint: function endpoint(user_id) {
                        return "/users/" + user_id;
                    }
                }
            },
            likes: {
                GET: {
                    endpoint: function endpoint(user_id) {
                        return "/users/" + user_id + "/likes";
                    }
                },
                PUT: {
                    endpoint: function endpoint(user_id, podcast_id) {
                        return "/users/" + user_id + "/likes/" + podcast_id;
                    }
                }
            },
            dislikes: {
                GET: {
                    endpoint: function endpoint(user_id) {
                        return "/users/" + user_id + "/dislikes";
                    }
                },
                PUT: {
                    endpoint: function endpoint(user_id, podcast_id) {
                        return "/users/" + user_id + "/likes/" + podcast_id;
                    }
                }
            },
            login: {
                POST: {
                    endpoint: function endpoint() {
                        return "/login";
                    }
                }
            },
            search: {
                GET: {
                    endpoint: function endpoint() {
                        var query = arguments.length <= 0 || arguments[0] === undefined ? {} : arguments[0];

                        var query_components = ["title", "author", "homepage", "day_of_week", "day_of_month", "length", "category", "published_since"];
                        var ep = "/search/podcasts";
                        var val = void 0;
                        if (Object.getOwnPropertyNames(query).length === 0) {
                            return ep;
                        } else {
                            ep += "?";
                            var _iteratorNormalCompletion = true;
                            var _didIteratorError = false;
                            var _iteratorError = undefined;

                            try {
                                for (var _iterator = query_components[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                                    var k = _step.value;

                                    if (val = query[k], val !== undefined) {
                                        ep += k + "=" + val + "&";
                                    }
                                    return ep.slice(0, -1);
                                }
                            } catch (err) {
                                _didIteratorError = true;
                                _iteratorError = err;
                            } finally {
                                try {
                                    if (!_iteratorNormalCompletion && _iterator.return) {
                                        _iterator.return();
                                    }
                                } finally {
                                    if (_didIteratorError) {
                                        throw _iteratorError;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    };
};
