// SPDX-License-Identifier: AGPL-3.0-only
inline int upstream_shell_check(){
    auto host_owner=std::make_unique<EngineHost>();auto& host=*host_owner;
    auto shell_owner=std::make_unique<Shell>(host);auto& shell=*shell_owner;auto& c=shell.context();
    for(auto& track:c.project.tracks)track.engine=EngineKind::Midi;
    c.ui.track=7;c.project.gen8.assign=1;c.project.gen8.group=1;
    c.prints.freeze[6].state=FreezeState::Deep;
    auto seed=c.project.gen8.seed;auto history=c.edits.size();c.gen8_action(0);
    if(c.ui.ask!=UiState::Ask::Unfreeze||c.ui.ask_target!=6||c.project.gen8.seed!=seed||c.edits.size()!=history)return 1;
    c.ui.ask=UiState::Ask::None;c.prints.freeze[6]={};
    c.track().engine=EngineKind::Plugin;c.track().plugin=0;std::strcpy(c.project.plugins[0].name,"Acid Engine");
    c.prints.freeze[7].state=FreezeState::Frozen;c.prints.freeze[7].set(0,true);
    auto acid_seed=c.track().acid_gen.seed;c.gen8_action(13);
    if(c.ui.ask!=UiState::Ask::None||c.track().acid_gen.seed!=acid_seed||c.edits.size()!=history)return 2;
    c.gen8_action(2);if(c.ui.ask!=UiState::Ask::Unfreeze||c.track().acid_gen.seed!=acid_seed)return 3;
    c.ui.ask=UiState::Ask::None;c.prints.freeze[7].state=FreezeState::Deep;edit_page.soft(c,2);
    if(c.ui.ask!=UiState::Ask::Unfreeze)return 6;
    c.ui.ask=UiState::Ask::None;c.track().engine=EngineKind::Sampler;c.track().break_bars=2;
    auto before=c.track().break_perf[0];c.apply(Binding{Binding::Kind::BreakPerfParam,0,0,127,0},100);
    if(c.ui.ask!=UiState::Ask::Unfreeze||c.track().break_perf[0]!=before)return 4;
    c.ui.ask=UiState::Ask::None;c.gen_break_load("/card/unopened.wav","unopened");
    if(c.ui.ask!=UiState::Ask::Unfreeze||c.ui.break_pending>=0)return 5;
    c.ui.ask=UiState::Ask::None;c.track().engine=EngineKind::Plugin;c.track().plugin=0;
    std::strcpy(c.project.plugins[0].path,"Plugins/RHYTHMER - Acid Engine");
    bool transport=c.project.plugins[0].transport;c.toggle_plugin_transport(0);
    if(c.ui.ask!=UiState::Ask::Unfreeze||c.project.plugins[0].transport!=transport)return 7;
    c.ui.page=PageId::PluginPresets;c.ui.presets_rows_count=2;c.ui.plugin_panel.programs=100;
    auto cards=page_bindings(c.project,c.ui,c.pattern());if(cards[0].max!=1)return 8;
    std::puts("RHYTHMER_UPSTREAM freeze_gen=guarded acid_auto=frozen_safe break_edit=guarded");
    return 0;
}
