import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';

const server_dl_url = "https://www.minecraft.net/en-us/download/server/" 
const default_ram = 1024;

// TODO
export class MCServer {

    // valid kwargs values: max_ram, min_ram, server_jar
    constructor(server_name, server_dir, kwargs) {
        this.server_name = server_name;
        this.server_dir = server_dir;
        this.eula_dir = kwargs.eula_dir ? kwargs.eula_dir : null;
        this.max_ram = kwargs.max_ram ? kwargs.max_ram : null;
        this.min_ram = kwargs.min_ram ? kwargs.min_ram : null;
        this.server_process = null;
    }

    update() {
        // TODO
    }

    start() {
        if (this._is_valid_server()) {
            this.server_process = spawn(
                'java', 
                [`-Xmx${this.max_ram ? this.max_ram : default_ram}M`, 
                `-Xms${this.min_ram ? this.min_ram : default_ram}M`, 
                '-jar', 
                `${this.server_jar}`, 
                'nogui'], 
                { cwd: this.server_dir }
                );
        }
    }

    stop() {
        console.log('stopping server');
        this.server_process.kill('SIGTERM');
    }

    restart() {
        this.stop();
        this.start();
    }

    // TODO
    setup() {
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
        fs.readFile(this.eula_dir, 'utf8', (err, data) => {
            if (err) {
                console.error(err);
                return;
            }
            // search and replace eula= to "accept" value
            let new_data = data.replace(/eula=false/g, `eula=${accept}`);
            // save eula.txt
            fs.writeFile(this.eula_dir, new_data, (err) => {
                if (err) {
                    console.error(err);
                    return;
                }
            });
        });
    }

    _is_valid_server() {
        // check if server_dir is valid
        if (!fs.existsSync(this.server_dir)) {
            return false;
        }

        // check if server jar exists
        if (!fs.existsSync(path.join([this.server_dir, this.server_jar]))) {
            return false;
        }

        // check if eula.txt file exists
        if (!fs.existsSync(this.eula_dir)) {
            return false;
        }

        return true;
    }
}