import Retriever from 'retriever';
import Dom from 'dom';

const init = () => {
    Retriever().attach(document.window);
    Dom().attach(document.window);
};
init();
