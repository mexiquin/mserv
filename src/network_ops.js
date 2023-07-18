import http from 'http';

// Searches a specified webpage searching for a hyperlink to a specified file
// Returns the url of the identified hyperlink
function scrape_file(url, search_file_name) {
    let requester = http.get(url);
    let text = requester.text;
    for (let link of text.findAll('a')) {
        if (link.get("href") !== null) {
            if (search_file_name in link.get("href")) {
                return link.get('href');
            }
        }
    }
}

// Downloads a file from a url and saves it in the specified output directory
// show progress bar of download
function download_file(url, output_dir) {
    let requester = http.get(url);
    let file_name = url.split('/').pop();
    let file = fs.createWriteStream(path.join([output_dir, file_name]));
    requester.pipe(file);
}

export { scrape_file, download_file };