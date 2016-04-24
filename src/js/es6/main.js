import Retriever from 'retriever';
import Dom from 'dom';

const init = () => {
    console.log("retriever");
    Retriever().attach(document.window);
    console.log("dom");
    Dom().attach(document.window);
};
init();
