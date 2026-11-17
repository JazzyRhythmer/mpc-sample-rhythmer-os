// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 jazzy rhythmer
#pragma once
#include <juce_audio_processors_headless/juce_audio_processors_headless.h>
#include "rhythmer/plugin/plugin_panel.h"
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace rhythmer {
// Original VSTs remain the synthesis/state authority. The loader runs only on
// the rack/control worker, and stages only the engine selected for a pad.
using SoundLoader = std::function<std::unique_ptr<juce::AudioPluginInstance>(const std::string&, juce::String&)>;
std::unique_ptr<juce::AudioPluginInstance> make_sound_rack(const juce::var& catalog,
    int single_engine, SoundLoader loader, double rate, int block, juce::String& error);
// Used by the existing parameter pages: no fixed truncation of original controls.
int sound_rack_parameter_count(juce::AudioPluginInstance*);
int sound_rack_source_parameter_begin(juce::AudioPluginInstance*);
std::vector<int> sound_rack_edit_order(juce::AudioPluginInstance*);
bool sound_rack_design_pages(juce::AudioPluginInstance*,PluginPanel&);
juce::String sound_rack_source_name(juce::AudioPluginInstance*);
juce::String sound_rack_preset_name(juce::AudioPluginInstance*);
bool sound_rack_drum_voices(juce::AudioPluginInstance*, DrumVoices&);
uint32_t sound_rack_revision(juce::AudioPluginInstance*);
int sound_rack_focus(juce::AudioPluginInstance*);
std::array<int,3> sound_rack_quick_parameters(juce::AudioPluginInstance*);
void sound_rack_set_parameter_checked(juce::AudioPluginInstance*,int,float,uint32_t);
bool is_sound_rack(juce::AudioPluginInstance*);
}
