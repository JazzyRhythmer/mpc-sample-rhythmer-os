// SPDX-License-Identifier: AGPL-3.0-only
// Integration check through Melodee's existing VST2 host, not a replacement host.
#include "rhythmer/plugin/vst2_instance.h"
#include "rhythmer/plugin/plugin_files.h"
#include "rhythmer/model/project_file.h"
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <filesystem>
#include <fstream>

static void scanner_test();

static void require(bool ok, const char* why) {
    if (!ok) throw std::runtime_error(why);
}

int main(int argc, char** argv) {
    try {
        require(argc >= 2, "Pass plugin folders");
        juce::ScopedJuceInitialiser_GUI init;
        scanner_test();
        for (int i = 1; i < argc; ++i) {
            auto file = rhythmer::describe_plugin(argv[i]);
            // This raw-DSP test reads source trigger maps separately from the
            // product browser, which advertises multi-sound pads only for Kit.
            if(file.single_drum){
                std::ifstream input(file.library,std::ios::binary);std::string bytes((std::istreambuf_iterator<char>(input)),{});file.drums=rhythmer::drum_voices_in(bytes);
                if(file.drums.empty()){std::ifstream map(std::filesystem::path(argv[i])/"drum-map.json");std::string data((std::istreambuf_iterator<char>(map)),{});file.drums=rhythmer::drum_voices_in(data);}
            }
            require(file.loadable(), file.why.c_str());
            require(file.fixed_rate == 44100, "Open MPC fixed-rate metadata missing");
            if (file.name == "TR-MPC") require(file.drums.size() == 16, "TR-MPC sidecar map missing");
            juce::String error;
            auto instance = rhythmer::Vst2Instance::load(juce::File(file.library), 44100, 128, error);
            require(bool(instance), error.toRawUTF8());
            instance->prepareToPlay(44100, 128);
            juce::AudioBuffer<float> audio(2, 256);
            juce::MidiBuffer midi;
            const auto render = [&](int frames) {
                audio.clear();
                audio.setSize(2, frames, false, false, true);
                instance->processBlock(audio, midi);
                midi.clear();
                double sum = 0;
                for (int c = 0; c < 2; ++c) for (int f = 0; f < frames; ++f) {
                    const float value = audio.getSample(c, f);
                    require(std::isfinite(value), "Non-finite output");
                    sum += double(value) * value;
                }
                return sum;
            };
            const int first = file.drums.empty() ? 60 : 36;
            const int count = file.drums.empty() ? 1 : int(file.drums.size());
            for (int pad = 0; pad < count; ++pad) {
                const int key = file.drums.empty() ? first : file.drums[size_t(pad)].key;
                midi.addEvent(juce::MidiMessage::allSoundOff(1), 0);
                midi.addEvent(juce::MidiMessage::noteOn(1, key, juce::uint8(110)), 7);
                double energy = 0;
                for (int b = 0; b < 64; ++b) energy += render(b % 2 ? 128 : 100);
                if (energy <= 0.00001)
                    std::cerr << instance->getName() << " note=" << key << " drums=" << file.drums.size() << '\n';
                require(energy > 0.00001, "Note/pad is silent");
            }
            juce::MemoryBlock state;
            instance->getStateInformation(state);
            require(state.getSize() > 0, "Empty state");
            auto project = std::make_unique<rhythmer::Project>();
            auto patterns = std::make_unique<rhythmer::PatternBank>();
            project->tracks[0].engine = rhythmer::EngineKind::Plugin;
            project->tracks[0].plugin = 0;
            const auto relative = "Plugins/" + std::filesystem::path(argv[i]).filename().string();
            std::snprintf(project->plugins[0].path, sizeof(project->plugins[0].path), "%s", relative.c_str());
            std::array<std::vector<uint8_t>, rhythmer::max_plugins> saved_states;
            const auto* bytes = static_cast<const uint8_t*>(state.getData());
            saved_states[0].assign(bytes, bytes + state.getSize());
            const auto encoded = rhythmer::save_project(*project, *patterns, &saved_states);
            auto loaded = std::make_unique<rhythmer::Project>();
            auto loaded_patterns = std::make_unique<rhythmer::PatternBank>();
            std::array<std::vector<uint8_t>, rhythmer::max_plugins> loaded_states;
            require(rhythmer::load_project(encoded, *loaded, *loaded_patterns, nullptr, &loaded_states).empty(), "Project load failed");
            require(loaded_states[0] == saved_states[0], "Project changed plugin state");
            require(relative == loaded->plugins[0].path, "Project changed plugin path");
            auto& params = instance->getParameters();
            require(!params.isEmpty(), "No parameters");
            // Open MPC appends transient popup controls after DSP parameters.
            // Test a stable DSP parameter, not the last UI-only open flag.
            auto* parameter = params[params.size() > 1 ? 1 : 0];
            const float before = parameter->getValue();
            auto twin=rhythmer::Vst2Instance::load(juce::File(file.library),44100,128,error);
            require(bool(twin),"Second independent instance failed");
            twin->prepareToPlay(44100,128);
            twin->setStateInformation(loaded_states[0].data(),int(loaded_states[0].size()));
            auto* twin_parameter=twin->getParameters()[params.size()>1?1:0];
            require(std::abs(twin_parameter->getValue()-before)<0.01f,"New instance did not restore saved controls");
            parameter->setValue(before > 0.5f ? 0.1f : 0.9f);
            render(128);
            require(std::abs(twin_parameter->getValue()-before)<0.01f,"Instances share mutable DSP controls");
            instance->setStateInformation(loaded_states[0].data(), int(loaded_states[0].size()));
            render(128);
            if (std::abs(parameter->getValue() - before) >= 0.01f)
                std::cerr << instance->getName() << ' ' << parameter->getName(64)
                          << " before=" << before << " restored=" << parameter->getValue() << '\n';
            require(std::abs(parameter->getValue() - before) < 0.01f, "State did not restore DSP parameter");
            twin->releaseResources();twin.reset();
            std::cout << "PASS " << instance->getName() << " params=" << params.size()
                      << " pads=" << count << " state_bytes=" << state.getSize()
                      << " project_bytes=" << encoded.size() << '\n';
            instance->releaseResources();
        }
    } catch (const std::exception& e) {
        std::cerr << "FAIL: " << e.what() << '\n';
        return 1;
    }
}

static void scanner_test() {
    namespace fs = std::filesystem;
    const fs::path folder = "/Volumes/SSD/Development/BuildCache/rhythmer-os/plugins/scanner-fixture";
    fs::create_directories(folder);
    { std::ofstream f(folder / "plugin-meta.xml"); f << "<PLUGIN name=\"Fixture\" file=\"test.so\" isInstrument=\"1\"/>"; }
    std::string elf(64, '\0');
    elf.replace(0, 5, "\x7f" "ELF\x02"); elf[18] = char(183);
    { std::ofstream f(folder / "test.so", std::ios::binary); f << elf; }
    const fs::path map = folder / "drum-map.json";
    const std::string valid = "{\"pad_layout\":\"drums\",\"levels\":{\"one\":{\"name\":\"Kick\",\"note\":36}}}";
    { std::ofstream f(map); f << valid; }
    require(rhythmer::describe_plugin(folder.string()).single_drum && rhythmer::describe_plugin(folder.string()).drums.empty(), "Single-sound source map classification failed");
    { std::ofstream f(map); f << "{broken"; }
    require(rhythmer::describe_plugin(folder.string()).drums.empty(), "Malformed sidecar accepted");
    { std::ofstream f(map); f << valid << std::string(65536, ' '); }
    require(rhythmer::describe_plugin(folder.string()).drums.empty(), "Oversized sidecar accepted");
    { std::ofstream f(map); f << valid; }
    { std::ofstream f(folder / "test.so", std::ios::binary); f << elf << "{\"pad_layout\":\"drums\",\"levels\":{\"old\":{\"name\":\"Embedded\",\"note\":40}}}"; }
    const auto embedded = rhythmer::describe_plugin(folder.string());
    require(embedded.single_drum && embedded.drums.empty(), "Embedded map escaped single-sound routing");
    fs::remove_all(folder);
    std::cout << "PASS sidecar scanner: valid, malformed, oversized, embedded precedence\n";
}
