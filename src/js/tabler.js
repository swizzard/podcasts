export default function (retriever, target) {
    const userId = retriever.userId,
          makeLink = (url, link) => $(`<a href="${url}">${link === undefined ? url : link}</a>`),
          setText = f => (val, node) => node.text(f(val)),
          setParseInt = setText(parseInt),
          setId = setText(x => x),
          setBool = setText(Boolean),
          weekDays = Symbol('weekDays'),
          models = Symbol('models'),
          makeHeader = Symbol('makeHeader'),
          makeContent = Symbol('makeContent'),
          makeEmpty = Symbol('makeEmpty'),
          getFavs = () => {
              let out = {likes: new Set(),
                         dislikes: new Set()},
                  res;
              ['likes', 'dislikes'].map(name => {
                retriever.GET(name, userId)
                    .on(resp => resp.json())
                    .on(js => {
                        if ((res = js.results, !!res)) {
                            res.map(p => out[name].add(p.id));
                        }
                    })
              });
              return out;
          },
          favCB = e => {
            let target = $(e.target),
                ep = target.data('ep'),
                podcastId = target.data('id'),
                toRemove = target.hasClass('active'),
                req = toRemove ? retriever.DELETE : retriever.PUT,
                f = toRemove ? t => { t.removeClass('active');
                                      t.attr('aria-pressed', 'false');} :
                               t => { t.addClass('active');
                                      t.attr('aria-pressed', 'true');};
                req(ep, userId, podcastId)
                  .on(resp => resp.json())
                  .on(js => {
                      if (!js.success) {
                          throw new Error(`${js.err}: ${js.args}`);
                      } else {
                          f(target);
                      }
                  })
                  .catch(err => { $(`<p class="bg-danger">${err}</p>`)
                                  .appendTo(target); });
          },
          tabler = {
            target: target,
            makeTable(model, result) {
                let tableId = 'resTable',
                    preexisting = $(`#${tableId}`),
                    likes, dislikes;
                if (preexisting.length) {
                    this.target.removeChild(preexisting);
                };
                let displayModel = this[models][model],
                    table = $((`<table id="${tableId}" class="table table-hover` +
                               'table-bordered"></table>')),
                    header = this[makeHeader](displayModel),
                    content = this[makeContent](displayModel, result);
                table.append(header);
                table.append(content);
                this.target.html(table);
                if (!!userId) {
                    favs = getFavs();
                    ['likes', 'dislikes'].map(l => {
                        $(`.fav[data-ep="${l}"]`).each((_, e) => {
                            let idx = e.data('id');
                            if (favs[l].has(idx)) {
                                e.addClass('active');
                                e.attr('aria-pressed', 'true')
                            }
                        })
                    })
                };
                table.on('click', '.fav', favCB);
            },
            [weekDays]: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday"],
            [models]: {
                Podcast: [
                    ["id", setParseInt],
                    ["title", setId],
                    ["feed_url", (val, node) => node.append(makeLink(val))],
                    ["language", setId],
                    ["episode_count", setParseInt],
                    ["explicit", setBool],
                    ["summary", setId]
                ],
                Episode: [
                    ["id", setParseInt],
                    ["date", setId],
                    ["title", setId],
                    ["podcast_id", setParseInt],
                    ["week_day", setText((wd) => this.weekDays[wd])],
                    ["day_of_month", setId]
                ],
                Category: [
                    ["id", setParseInt],
                    ["name", setId]
                ],
                User: [
                    ["id", setParseInt],
                    ["name", setId],
                    ["email", setId],
                    ["public", setBool]
                ]
            },
            [makeHeader](displayModel) {
                let col, th;
                const thead = this[makeEmpty]('thead');
                const tr = this[makeEmpty]('tr');
                for (col of displayModel) {
                    th = this[makeEmpty]('th');
                    th.text(col[0]);
                    th.appendTo(tr);
                };
                if (displayModel[2] === 'feed_url' && retriever.loggedIn()) {
                    let favTh = this[makeEmpty]('th'),
                        unFavTh = this[makeEmpty]('th');
                    favTh.text('like');
                    unFavTh.text('dislike');
                    favTh.appendTo(tr);
                    unFavTh.appendTo(tr);
                };
                thead.append(tr);
                return thead;
            },
            [makeContent](displayModel, data) {
                let fn, label, key, row, td, tr, val;
                const tbody = this[makeEmpty]('tbody'),
                      showFav = (displayModel[2] === 'feed_url' &&
                                 retriever.loggedIn());
                for (row of data) {
                    tr = this[makeEmpty]('tr');
                    for ([label, fn] of displayModel) {
                        td = this[makeEmpty]('td');
                        fn(row[label], td);
                        td.appendTo(tr);
                    };
                    if (showFav) {
                        let favTd = this[makeEmpty]('td'),
                            unFavTd = this[makeEmpty]('td'),
                            favButton = $(('<button class="btn btn-success fav" ' +
                                           `data-id="${row.id}" data-ep="likes">`  +
                                           'like this</button>')),
                            unFavButton = $(('<button class="btn btn-warning fav" ' +
                                             `data-id="${row.id}" data-ep="dislikes">` +
                                             'dislike this</button>'));
                        favTd.append(favButton).appendTo(tr);
                        unFavTd.append(unFavButton).appendTo(tr);
                    };
                    tbody.append(tr);
                }
                return tbody;
            },
            [makeEmpty](name) {
                return $(`<${name}></${name}>`);
            }
    };
        return tabler;
};
