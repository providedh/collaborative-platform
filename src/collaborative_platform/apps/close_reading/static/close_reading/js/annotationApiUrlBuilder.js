const API_urls = {
    get_save_url : (project, file) => [
        window.location.protocol + '/',
        window.location.hostname+':5000', 
        'api/v1/project', 
        project, 
        'teiclose', 
        file, 
        'save/'].join('/'),
    get_add_annotation_url : (project, file) => [
        window.location.protocol + '/',
        window.location.hostname+':5000', 
        'api/v1/project', 
        project, 
        'teiclose', 
        file, 
        'annotate/'].join('/'),
    get_history_url : (project, file, version) => [
        window.location.protocol + '/',
        window.location.hostname+':5000', 
        'api/v1/project', 
        project, 
        'teiclose', 
        file, 
        version, 
        'annotationhistory/'].join('/'),
    get_autocomplete_url : (project, entity_type, query) => [
        window.location.protocol + '/',
        window.location.hostname+':5000', 
        'api/v1/fuzzysearch', 
        project, 
        entity_type, 
        query].join('/')
};

module.exports = {
    API_urls
};
