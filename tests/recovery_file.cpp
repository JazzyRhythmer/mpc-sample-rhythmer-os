// SPDX-License-Identifier: AGPL-3.0-only
#include "shell/recovery_file.h"
#include <cassert>
#include <iostream>
#include <set>
#include <csignal>
#include <sys/resource.h>
#include <sys/wait.h>

using namespace rhythmer;
namespace fs=std::filesystem;
static std::vector<uint8_t> read(const fs::path& p){std::ifstream f(p,std::ios::binary);return {std::istreambuf_iterator<char>(f),{}};}
int main(int argc,char** argv){
    assert(argc==2);const auto dir=fs::absolute(argv[1]);fs::create_directories(dir);
    std::set<std::string> ids;
    for(unsigned n=0;n<1000;++n){auto id=recovery_file::new_id();assert(recovery_file::valid_id(id));assert(ids.insert(id).second);}
    assert(recovery_file::legacy_id("/a/Song.mldp")==recovery_file::legacy_id("/a/./Song.mldp"));
    assert(recovery_file::legacy_id("/a/Song.mldp")!=recovery_file::legacy_id("/b/Song.mldp"));
    assert(!recovery_file::valid_id("../Song"));
    const auto file=dir/"checkpoint.mldp";const std::vector<uint8_t> old{'o','l','d'};
    assert(recovery_file::atomic_write(file.string(),old).empty());
    // Real write failure after a short write must leave the old file intact.
    pid_t child=fork();assert(child>=0);
    if(!child){std::signal(SIGXFSZ,SIG_IGN);rlimit limit{10,10};assert(!setrlimit(RLIMIT_FSIZE,&limit));
        auto error=recovery_file::atomic_write(file.string(),std::vector<uint8_t>(20000,7));_exit(error.empty()?1:0);}
    int status=0;waitpid(child,&status,0);assert(WIFEXITED(status)&&WEXITSTATUS(status)==0);
    assert(read(file)==old&&!fs::exists(file.string()+".new"));
    // An interrupted staging write cannot become the checkpoint automatically.
    {std::ofstream f(file.string()+".new");f<<"interrupted";}
    assert(read(file)==old);
    assert(recovery_file::atomic_write(file.string(),{'n','e','w'}).empty());
    assert(read(file)==std::vector<uint8_t>({'n','e','w'}));
    std::vector<uint8_t> manifest(8,0);recovery_file::append_origin(manifest,"/card/Music/Song.mldp");
    recovery_file::append_text(manifest,"RCMP","a");
    assert(recovery_file::origin(manifest)=="/card/Music/Song.mldp");
    assert(recovery_file::media_path(file.string(),manifest)==(dir/".checkpoint-a/state.mldp").string());
    assert(recovery_file::atomic_write(file.string(),manifest).empty());
    assert(recovery_file::next_slot(file.string())=="b");
    auto truncated=manifest;truncated.resize(13);assert(recovery_file::origin(truncated).empty());
    const auto source=dir/"Source Audio";fs::create_directories(source);
    {std::ofstream f(source/"take.wav");f<<"first take";}
    assert(recovery_file::copy_media((dir/"Source.mldp").string(),(dir/"Copy.mldp").string()).empty());
    assert(read(source/"take.wav")==read(dir/"Copy Audio/take.wav"));
    // Same-size changed audio must not be skipped as an already copied file.
    {std::ofstream f(source/"take.wav");f<<"other take";}
    fs::last_write_time(source/"take.wav",fs::file_time_type::clock::now()+std::chrono::seconds(5));
    assert(recovery_file::copy_media((dir/"Source.mldp").string(),(dir/"Copy.mldp").string()).empty());
    assert(read(source/"take.wav")==read(dir/"Copy Audio/take.wav"));
    const auto root=dir/"card/Rhythmer/Projects";fs::create_directories(root);
    assert(recovery_file::protected_folder(dir/"card/Rhythmer/Autosave",root.string()));
    assert(recovery_file::protected_folder(dir/"card/autorun",root.string()));
    assert(!recovery_file::protected_folder(dir/"card/Music",root.string()));
    std::cout<<"RECOVERY_FILE_OK identities=1000 write_failure=preserved media=verified\n";
}
