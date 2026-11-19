// SPDX-License-Identifier: AGPL-3.0-only
#pragma once
// File operations here run on the service thread, never the audio callback.
#include <array>
#include <atomic>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <random>
#include <string>
#include <vector>
#include <fcntl.h>
#include <unistd.h>

namespace rhythmer::recovery_file {
inline uint64_t hash(const std::vector<uint8_t>& bytes) {
    uint64_t h = 14695981039346656037ull;
    for (auto c : bytes) { h ^= c; h *= 1099511628211ull; }
    return h;
}
inline bool valid_id(const std::string& s) {
    if (s.size() != 32) return false;
    for (auto c : s) if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    return true;
}
inline std::string new_id() {
    std::random_device random;
    char out[33];
    for (unsigned n = 0; n < 4; ++n) std::snprintf(out + n*8, 9, "%08x", unsigned(random()));
    return out;
}
inline std::string legacy_id(const std::string& path) {
    // Legacy files have no embedded ID yet. Their full, normalized paths distinguish equal names.
    const auto text = std::filesystem::path(path).lexically_normal().string();
    std::vector<uint8_t> bytes(text.begin(), text.end());
    const auto a = hash(bytes); bytes.push_back(0x52); const auto b = hash(bytes);
    char out[33]; std::snprintf(out, sizeof out, "%016llx%016llx", (unsigned long long)a, (unsigned long long)b);
    return out;
}
inline bool under(const std::filesystem::path& path, const std::filesystem::path& root) {
    auto p = path.lexically_normal(), r = root.lexically_normal();
    auto a = p.begin(), b = r.begin();
    for (; b != r.end(); ++a, ++b) if (a == p.end() || *a != *b) return false;
    return true;
}
inline bool protected_folder(const std::filesystem::path& dir, const std::string& root) {
    namespace fs = std::filesystem;
    const auto app = fs::path(root).parent_path();
    const auto card = app.parent_path();
    for (const auto& p : {app/"Autosave", app/"Cache", app/"Crashes", app/"Plugins", card/"autorun", card/"MPC-Sample"})
        if (under(dir, p)) return true;
    // Symlinks must not turn a valid displayed path into an out-of-card write.
    std::error_code e;
    auto resolved = fs::weakly_canonical(dir, e);
    if (e || !under(resolved, fs::weakly_canonical(card, e)) || e) return true;
    for (const auto& p : {app/"Autosave", app/"Cache", app/"Crashes", app/"Plugins", card/"autorun", card/"MPC-Sample"}) {
        const auto protected_path=fs::weakly_canonical(p,e);
        if(e||under(resolved,protected_path))return true;
    }
    return false;
}
inline void append_text(std::vector<uint8_t>& bytes, const char* tag, const std::string& text) {
    bytes.insert(bytes.end(), tag, tag+4);
    const uint32_t n = uint32_t(text.size());
    for (unsigned i=0; i<4; ++i) bytes.push_back(uint8_t(n >> (i*8)));
    bytes.insert(bytes.end(), text.begin(), text.end());
}
inline void append_origin(std::vector<uint8_t>& bytes, const std::string& text) { append_text(bytes,"RCVR",text); }
inline std::string text_chunk(const std::vector<uint8_t>& bytes, const char* tag) {
    std::string found;
    for (size_t at=8; at+8<=bytes.size();) {
        uint32_t n=0; for(unsigned i=0;i<4;++i)n|=uint32_t(bytes[at+4+i])<<(i*8);
        if (n>bytes.size()-at-8) return {};
        if (!std::memcmp(bytes.data()+at,tag,4)) found.assign(bytes.begin()+at+8,bytes.begin()+at+8+n);
        at += 8+n;
    }
    return found;
}
inline std::string origin(const std::vector<uint8_t>& bytes) {return text_chunk(bytes,"RCVR");}
inline std::string media_path(const std::string& checkpoint, const std::vector<uint8_t>& bytes) {
    const auto slot=text_chunk(bytes,"RCMP");
    if(slot!="a"&&slot!="b")return checkpoint;
    const auto p=std::filesystem::path(checkpoint);
    return (p.parent_path()/("."+p.stem().string()+"-"+slot)/"state.mldp").string();
}
inline std::string next_slot(const std::string& checkpoint) {
    std::ifstream file(checkpoint,std::ios::binary);
    const std::vector<uint8_t> bytes{std::istreambuf_iterator<char>(file),{}};
    return text_chunk(bytes,"RCMP")=="a"?"b":"a";
}
inline std::string atomic_write(const std::string& path, const std::vector<uint8_t>& bytes) {
    namespace fs = std::filesystem;
    std::error_code error;
    fs::create_directories(fs::path(path).parent_path(), error);
    if (error) return "Could not create save folder";
    const auto temporary = path + ".new";
    int fd = ::open(temporary.c_str(), O_CREAT|O_TRUNC|O_WRONLY, 0600);
    if (fd<0) return "Could not write project";
    size_t at=0; bool ok=true;
    while(at<bytes.size()) {
        auto n=::write(fd,bytes.data()+at,bytes.size()-at);
        if(n<0&&errno==EINTR)continue;
        if(n<=0){ok=false;break;} at+=size_t(n);
    }
    if(ok&&::fsync(fd)!=0)ok=false;
    if(::close(fd)!=0)ok=false;
    if(!ok){fs::remove(temporary,error);return "Could not finish project save";}
    fs::rename(temporary,path,error);
    if(error){fs::remove(temporary,error);return "Could not replace project";}
    int parent=::open(fs::path(path).parent_path().c_str(),O_RDONLY|O_DIRECTORY);
    if(parent>=0){::fsync(parent);::close(parent);} // some removable filesystems do not support directory fsync
    return {};
}
inline std::string copy_media(const std::string& from, const std::string& to, bool copy_loops = false) {
    namespace fs=std::filesystem;
    for(const char* suffix:{" Prints"," Audio"," Loops"}) {
        if(!copy_loops&&std::string(suffix)==" Loops")continue;
        const auto source=fs::path(from).parent_path()/(fs::path(from).stem().string()+suffix);
        const auto target=fs::path(to).parent_path()/(fs::path(to).stem().string()+suffix);
        std::error_code error;
        if(!fs::is_directory(source,error)) {if(error&&error!=std::errc::no_such_file_or_directory)return "Could not read project media";continue;}
        fs::create_directories(target,error);if(error)return "Could not create media folder";
        for(const auto& entry:fs::directory_iterator(source,error)) {
            if(!entry.is_regular_file(error)||entry.path().extension()==".part")continue;
            const auto destination=target/entry.path().filename();
            // Takes/prints are immutable. Preserve existing completed copies and avoid a full recopy every idle save.
            if(fs::is_regular_file(destination,error)&&fs::file_size(destination,error)==entry.file_size(error)&&
               fs::last_write_time(destination,error)==entry.last_write_time(error)&&!error)continue;
            auto temporary=destination.string()+".new";
            // Buffered I/O also works on card/VM filesystems without copy_file_range support.
            const int source_fd=::open(entry.path().c_str(),O_RDONLY);
            if(source_fd<0)return "Could not read project media";
            const int target_fd=::open(temporary.c_str(),O_CREAT|O_TRUNC|O_WRONLY,0600);
            if(target_fd<0){::close(source_fd);return "Could not create copied media";}
            std::array<uint8_t,65536> buffer{};bool ok=true;
            for(;;){
                const auto count=::read(source_fd,buffer.data(),buffer.size());
                if(count<0&&errno==EINTR)continue;
                if(count<0){ok=false;break;}
                if(!count)break;
                size_t at=0;
                while(at<size_t(count)){
                    const auto n=::write(target_fd,buffer.data()+at,size_t(count)-at);
                    if(n<0&&errno==EINTR)continue;
                    if(n<=0){ok=false;break;}at+=size_t(n);
                }
                if(!ok)break;
            }
            ::close(source_fd);
            if(ok&&::fsync(target_fd)!=0)ok=false;
            if(::close(target_fd)!=0)ok=false;
            if(!ok){fs::remove(temporary,error);return "Could not finish media copy";}
            fs::rename(temporary,destination,error);if(error)return "Could not publish project media";
            fs::last_write_time(destination,entry.last_write_time(error),error);
        }
        if(error)return "Could not read project media";
    }
    return {};
}
inline bool replace_chunk(std::vector<uint8_t>& bytes,const char* tag,const std::string& value) {
    if(bytes.size()<8)return false;
    std::vector<uint8_t> next(bytes.begin(),bytes.begin()+8);
    for(size_t at=8;at<bytes.size();) {
        if(at+8>bytes.size())return false;
        uint32_t n=0;for(unsigned i=0;i<4;++i)n|=uint32_t(bytes[at+4+i])<<(i*8);
        if(n>bytes.size()-at-8)return false;
        if(std::memcmp(bytes.data()+at,tag,4))next.insert(next.end(),bytes.begin()+at,bytes.begin()+at+8+n);
        at+=8+n;
    }
    append_text(next,tag,value);bytes=std::move(next);return true;
}
inline std::string pin_legacy_identity(const std::string& path, const std::string& display_name = {}) {
    std::ifstream in(path,std::ios::binary);
    std::vector<uint8_t> bytes{std::istreambuf_iterator<char>(in),{}};
    if(bytes.size()<8||std::memcmp(bytes.data(),"MELODEE1",8))return "Could not identify project";
    const auto raw=text_chunk(bytes,"RID1");
    const bool identified=raw.size()==33&&raw[0]==32&&valid_id(raw.substr(1));
    if(identified&&display_name.empty())return {};
    // Explicit Rename/Move keeps legacy identity without changing its musical state.
    if(!identified&&!replace_chunk(bytes,"RID1",std::string(1,char(32))+legacy_id(path)))return "Invalid project identity";
    if(!display_name.empty()) {
        const auto original=text_chunk(bytes,"PROJ");
        if(original.empty()||size_t(uint8_t(original[0]))+1>original.size())return "Invalid project name";
        const auto shown=display_name.substr(0,31);
        const auto value=std::string(1,char(shown.size()))+shown+original.substr(size_t(uint8_t(original[0]))+1);
        if(!replace_chunk(bytes,"PROJ",value))return "Invalid project data";
    }
    return atomic_write(path,bytes);
}
} // namespace rhythmer::recovery_file
