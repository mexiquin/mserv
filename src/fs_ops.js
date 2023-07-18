import fs from 'fs';

function identify_servers(directory) {
    // Identify any potential servers (top-level subdirectories) in the given directory
    // Returns a list of server directories relative to the given directory
    let servers = [];
    fs.readdirSync(directory).forEach(file => {
        if (fs.statSync(file).isDirectory()) {
            servers.push(file);
        }
    });

    return servers;
    
}

function search_and_replace_file(file, search, replace) {
    let file_data = fs.readFileSync(file, 'utf8');
    let new_file_data = file_data.replace(search, replace);
    fs.writeFileSync(file, new_file_data, 'utf8');
    return file_data.split(search).length - 1;
}