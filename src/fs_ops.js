import fs from 'fs';

export function identify_servers(directory) {
    let servers = [];
    fs.readdirSync(directory).forEach(file => {
        if (fs.statSync(file).isDirectory()) {
            servers.push(file);
        }
    });

    return servers;
    
}

export function search_and_replace_file(file, search, replace) {
    let file_data = fs.readFileSync(file, 'utf8');
    let new_file_data = file_data.replace(search, replace);
    fs.writeFileSync(file, new_file_data, 'utf8');
    return file_data.split(search).length - 1;
}