"""Keep upstream's finite instance pool from returning a silent instrument.

The original DSP, pool size and parameter/state implementation are unchanged.
An exhausted pool rejects the new load, allowing Rhythmer to keep the old track.
This transformation applies to a generated build copy, never the pinned source.
"""

def apply(source):
    anchor='class Frodhes : public mpc::Plugin\n{\npublic:\n'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+'''    bool rhythmerReady() const { return in_ && frp_inst_slot(in_) >= 0; }
''',1)
    anchor='MPC_PLUGIN_ENTRY(Frodhes)'
    assert source.count(anchor)==1
    return source.replace(anchor,'''// Rhythmer host load guard; original sound engine and preset/state code above.
extern "C" MPC_EXPORT AEffect* VSTPluginMain(audioMasterCallback host)
{
    if (host && host(nullptr, audioMasterVersion, 0, 0, nullptr, 0.0f) == 0)
        return nullptr;
    Frodhes *plugin = nullptr;
    try {
        plugin = new Frodhes();
        if (!plugin->rhythmerReady()) { delete plugin; return nullptr; }
        return mpc::detail::createEffect(plugin, host);
    } catch (...) { delete plugin; return nullptr; }
}
''',1)
