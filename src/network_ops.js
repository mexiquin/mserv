import http from 'http';

export function scrape_file_keyword(url, search_file_name) {
    let requester = http.get(url);
    let text = requester.text;
    for (let link of text.findAll('a')) {
        if (link.get("href") !== null) {
            if (search_file_name in link.get("href")) {
                return {link: link.get('href'), name: link.text};
            }
        }
    }
}

export function download_file(url, output_dir) {
    let requester = http.get(url);
    let file_name = url.split('/').pop();
    let file = fs.createWriteStream(path.join([output_dir, file_name]));
    requester.pipe(file);
}
