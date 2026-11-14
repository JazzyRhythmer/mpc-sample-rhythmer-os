// SPDX-License-Identifier: AGPL-3.0-only
// Rhythmer entry point: the sample-base runtime (base/src/runtime/) hosting
// RhythmerApp, plus Rhythmer's own tools (--self-test, previews, sound check).
#include "runtime/app.h"
#include "runtime/control_socket.h"
#include "runtime/inventory.h"
#include "runtime/options.h"
#include "runtime/run_app.h"
#include "rhythmer/rhythmer_app.h"
#include "rhythmer/tools.h"
#include <sys/stat.h>
#include <exception>
#include <iostream>
#include <memory>
#include <stdexcept>

int main(int argc, char** argv) {
    umask(0077);
    try {
        if (auto code = rhythmer::run_tool(argc, argv)) return *code;
        auto options = parse_options(argc, argv, "rhythmer");
        switch (options.mode) {
        case Options::Mode::Run: {
            if (options.app != "rhythmer") throw std::runtime_error("This build runs only Rhythmer, not " + options.app);
            auto app = std::make_unique<RhythmerApp>(); // Large: keep it off the stack.
            return run_app(*app, options);
        }
        case Options::Mode::Control: return send_control_command(options.runtime, options.command);
        case Options::Mode::ControlStream: return stream_control_commands(options.runtime);
        case Options::Mode::Hardware: return print_hardware();
        }
    } catch (const std::exception& error) {
        std::cerr << "rhythmer: " << error.what() << '\n';
    }
    return 1;
}
