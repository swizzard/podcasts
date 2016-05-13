import moment from 'moment';

const inputClass = "search-input";
const formId = 'search-form';

function showErr(msg) {
    console.log(`err: ${msg}`);
    $("#top").append(`<p id="input-err" class="bg-danger">${msg}</p>`);
};

function makeAutocompleteInput(queryName, placeholder="whatever", label=null) {
    return `<label for="input-${queryName}" class="sr-only">
                ${!!label ? label : queryName}
            </label>
            <input type="text" autocomplete="off" id="input-${queryName}"
                placeholder=${placeholder} class="${inputClass}" form="${formId}"
                data-query="${queryName}"/>`
};

function addAutocomplete(dataTarget, model) {
    const homepage = "http://localhost:8000";
    let ep = `${homepage}/autocomplete/${model}`,
        target = document.getElementById(`input-${model}`);
    fetch(ep)
        .then(resp => resp.json())
        .then(res => {
            let list = res['result'];
            return new Awesomplete(target, {list});
        })
        .then(() => {
            $(target).on('awesomplete-select',
                e => { 
                    let val = e.originalEvent.text.value;
                    if (!!e) dataTarget[model] = val;
                    return true;
                })
        })
        .catch(err => {
            showErr(err.messge);
        });
};

function makeSelectInput(queryName, choices, selectedChoice=null) {
    let selects = '', choice, val;
    for ([choice, val] in choices) {
        selects += `\n<option value="${val}"
                        ${(choice === selectedChoice) ? " selected" : ""}>
                        ${choice}
                        </option>`
    }
    return `<select form=${formId} class=${inputClass}
                data-query="${queryName}">${selects}\n</select>`
};

export default function(retriever, tabler, target) {
    const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
                        'Friday', 'Saturday'].map((v, i) => [v, i]);
    let   daysOfMonth = [];
    for (let i = 1; i < 32; i++) {
        daysOfMonth.push([moment({y: 2016, M: 4, d: i}).format('Do'), i]);
    };
    let   root = $('<div class="col-lg-12" id="root"></div>'),
          form = $(`<form class="form-inline hidden" id="${formId}"></form>`),
          catSelector = makeAutocompleteInput('category'),
          authSelector = makeAutocompleteInput('author', 'whoever'),
          txt = $(`<span class="searcher">I want a podcast that</span>`),
          moar = $('<button type="button" class="btn btn-link" id="moar">&hellip;</button>'),
          opts, moarSet, addAnd, selected, query;

    function init() {
        $("#root").remove();
        opts = {'--': null,
                'is about': ` is about ${catSelector}`,
                'published recently':
                (' <button class="btn btn-primary ' +
                `${inputClass}" data-query="published_since" ` +
                'id="publishedSince">is published recently </button>'),
                'is published on (weekday)':
                ` is published on ${makeSelectInput('day_of_week', daysOfWeek)}`,
                'is published on (day of month)':
                ` is published on ${makeSelectInput('day_of_month', daysOfMonth)}`,
                'is at least so long':
                ` is at least ${makeAutocompleteInput('length', 'min')} minutes long`,
                'is made by':
                ` is made by ${authSelector}`,
                '.': '.'
                },
        moarSet = false,
        addAnd = false,
        selected = new Set(),
        query = {};
        target.append(form);
        target.append(root.append(txt.append(moar)));
    };

    function optsSelector() {
        let optElems = [], opt;
        for (opt of Object.keys(opts)) {
            if (!selected.has(opt)) {
                optElems.push(`<option value="${opt}">${opt}</option>`);
            };
        };
        return ` <select id="opts-selector" form="${formId}">\n
                    ${optElems.join('\n')}
                \n</select>`
    };
    const optCB = e => {
        let target = $(e.target),
            qname = target.prev().data('query'),
            toDel = target.parents('.opt');
        if (!!selected.delete(qname)) {
            delete query[qname];
        };
        toDel.remove();
    };
    const pubSinceCB = e => {
        let target = $(e.target),
            since = moment().subtract(2, 'weeks').format('YYYY-MM-DD');
        if (target.hasClass('active')) {
            target.removeClass('active');
            delete query['published_since'];
        } else {
            target.addClass('active');
            target.attr('aria-pressed', 'true');
            query['published_since'] = since;
        }
    };
    const inputCB = e => {
        let target = $(e.target),
            val = e.target.value,
            qname = target.data().query;
        $('#input-err').remove();
        if (qname === 'length') {
            if (!$.isNumeric(val)) {
                showErr('Length must be in minutes!');
            }
        }
        query[qname] = val;
    };
    const optSelectorCB = e => {
        let val = e.target.value,
            closeButton = ('<button type="button" class="btn btn-danger btn-xs x"' +
                           'aria-label="Close"><span aria-hidden="true">' +
                           '&times;</span></button>'),
            queryDone = (val === '.'),
            opt, toInsert;
        $('#input-err').remove();
        if ((opt = opts[val]), (!opt)) {
            return false;
        }
        toInsert = '';
        if (!queryDone) {
            if (!addAnd) {
                addAnd = true;
            } else {
                toInsert = '<span class="amp">&nbsp;&amp;&nbsp;</span>';
            }
        };
        toInsert += (`<span class="opt">${opt}` +
                     (queryDone ? '' : closeButton) +
                     '</span>');
        $("#moar").before(toInsert);
        $("#opts-selector").remove();
        if (queryDone) {
            let res = retriever.POST('search', query),
                resetButton = $(('<button type="button" class="btn btn-danger btn-xs"' +
                                 ' id="reset"><small>&olarr; RESET</small></button>')),
                err;
            $(target).append(resetButton);
            $("#reset").on(() => init());
            res.then(resp => {
                if (!!resp.model) {
                    tabler.makeTable(resp.model, resp.result);
                } else {
                    showErr(`bad response: ${resp}`);
                }}).catch(err => showErr(err));
            return false;
        } else {
            switch (val) {
                case 'published recently':
                    $("#publishedSince")
                        .on('click', pubSinceCB)
                        .click();
                    break;
                case 'is made by':
                    addAutocomplete(query, 'author');
                    break;
                case 'is about':
                    addAutocomplete(query, 'category');
                    break;
                default:
                    $(`.${inputClass}`).on('change', inputCB);
                };
            $(".x").on('click', optCB);
            selected.add(val);
            moarSet = false;
            $("#moar").show();
        }
    };
    const moarCB = e => {
        let target = $(e.target);
        if (moarSet) {
            return false
        } else {
            let remainingKeys = Object.keys(opts).filter(v => !selected.has(v));
            moarSet = true;
            if (!!remainingKeys.length) {
                target.before(optsSelector());
                target.hide();
                };
                $("#opts-selector").on('change', optSelectorCB)
            }
        }
    init();
    $("#moar").on('click', moarCB);
};
