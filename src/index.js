import path from 'path';
import fs from 'fs';

// url of the minecraft server download page
const url = "https://www.minecraft.net/en-us/download/server/" 

// TODO
class MCServer {

    // valid kwargs values: max_ram, min_ram, server_jar
    constructor(server_name, server_dir, kwargs) {
        this.server_name = server_name;
        this.server_dir = server_dir;
        this.eula_dir = kwargs.eula_dir ? kwargs.eula_dir : null;
        this.max_ram = kwargs.max_ram ? kwargs.max_ram : null;
        this.min_ram = kwargs.min_ram ? kwargs.min_ram : null;
    }

    update() {
        // TODO
    }

    start() {
        // TODO
    }

    stop() {
        // TODO
        // graceful shutdown server
        // if server is not shutdown in 15 seconds, force shutdown
    }

    restart() {
        // TODO
        // graceful shutdown server
        // start server
    }

    setup() {
        // TODO
        // download server to server_dir
        // execute server jar for first time
        // accept eula
        // setup complete
    }

    set_eula_dir(dir) {
        if (dir) {
            this.eula_dir = dir;
        } else if (path.join([this.server_dir, 'eula.txt'])) {
            this.eula_dir = path.join([this.server_dir, 'eula.txt']);
        } else {
            this.eula_dir = null;
        }
    }

    update_eula(accept=true) {
        // TODO
        // open eula.txt
        // change eula= to "accept" value
        // save eula.txt

    }

    is_valid_server() {
        // TODO
    }
}