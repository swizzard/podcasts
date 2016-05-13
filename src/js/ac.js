export default function (dataTarget, input, model) {
    const homepage = "http://localhost:8000";
        let ep = `${homepage}/autocomplete/${model}`;
        fetch(ep)
            .then((resp) => {
                let res = JSON.parse(resp),
                    opts = {list: res['results'],
                            replace: (txt) => (txt === "whatever" || txt === "whenever") ? null : txt}
                return new Awesomeplete(input, opts);
            })
            .then((ac) => {
                ac.on('awesomeplete-selectcomplete',
                        (e) => { if (!!e) dataTarget[model] = e.text })
            })
            .catch((err) => {
                let errMsg = document.createElement(
                        `<div class="alert alert-danger" role="alert">
                            ${err}
                        </div>`);
                errMsg.appendTo(input.parent());
                return false;
            });
    };
