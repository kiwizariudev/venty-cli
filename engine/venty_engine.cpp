#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <filesystem>
#include <chrono>
#include <algorithm>
#include <cstring>

namespace fs = std::filesystem;

static void print_usage() {
    std::cout << "venty_engine <command> [args...]\n"
              << "  stat    <path>           file/dir info\n"
              << "  hash    <path>           SHA-256 of file\n"
              << "  count   <path> [ext]     count files (optional extension filter)\n"
              << "  lines   <path> [ext]     count lines of code\n"
              << "  size    <path>           total size of directory in bytes\n"
              << "  find    <path> <pattern> find files matching pattern\n"
              << "  newer   <path> <seconds> files modified in last N seconds\n"
              << "  dupes   <path>           find duplicate files by size\n"
              << "  tree    <path> [depth]   print directory tree\n"
              << "  ping    <host>           fast ICMP ping check (Windows)\n";
}

static std::string file_sha256(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) return "error: cannot open file";
    uint32_t h[8] = {
        0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
        0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19
    };
    const uint32_t k[64] = {
        0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
        0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
        0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
        0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
        0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
    };
    auto rotr = [](uint32_t x, int n){ return (x >> n) | (x << (32-n)); };
    std::vector<uint8_t> data;
    char buf[4096];
    while (f.read(buf, sizeof(buf)) || f.gcount())
        data.insert(data.end(), buf, buf + f.gcount());
    uint64_t bit_len = data.size() * 8;
    data.push_back(0x80);
    while (data.size() % 64 != 56) data.push_back(0);
    for (int i = 7; i >= 0; i--) data.push_back((bit_len >> (i*8)) & 0xff);
    for (size_t i = 0; i < data.size(); i += 64) {
        uint32_t w[64];
        for (int j = 0; j < 16; j++)
            w[j] = (data[i+j*4]<<24)|(data[i+j*4+1]<<16)|(data[i+j*4+2]<<8)|data[i+j*4+3];
        for (int j = 16; j < 64; j++) {
            uint32_t s0 = rotr(w[j-15],7)^rotr(w[j-15],18)^(w[j-15]>>3);
            uint32_t s1 = rotr(w[j-2],17)^rotr(w[j-2],19)^(w[j-2]>>10);
            w[j] = w[j-16]+s0+w[j-7]+s1;
        }
        uint32_t a=h[0],b=h[1],c=h[2],d=h[3],e=h[4],f2=h[5],g=h[6],hh=h[7];
        for (int j = 0; j < 64; j++) {
            uint32_t S1=rotr(e,6)^rotr(e,11)^rotr(e,25);
            uint32_t ch=(e&f2)^(~e&g);
            uint32_t t1=hh+S1+ch+k[j]+w[j];
            uint32_t S0=rotr(a,2)^rotr(a,13)^rotr(a,22);
            uint32_t maj=(a&b)^(a&c)^(b&c);
            uint32_t t2=S0+maj;
            hh=g; g=f2; f2=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
        }
        h[0]+=a; h[1]+=b; h[2]+=c; h[3]+=d;
        h[4]+=e; h[5]+=f2; h[6]+=g; h[7]+=hh;
    }
    std::ostringstream ss;
    for (int i = 0; i < 8; i++) ss << std::hex << std::setw(8) << std::setfill('0') << h[i];
    return ss.str();
}

static void cmd_stat(const std::string& path) {
    std::error_code ec;
    auto st = fs::status(path, ec);
    if (ec) { std::cout << "error: " << ec.message() << "\n"; return; }
    std::cout << "path    : " << path << "\n";
    std::cout << "type    : " << (fs::is_directory(st) ? "directory" : fs::is_regular_file(st) ? "file" : "other") << "\n";
    if (fs::is_regular_file(st)) {
        std::cout << "size    : " << fs::file_size(path, ec) << " bytes\n";
    }
    auto lwt = fs::last_write_time(path, ec);
    if (!ec) {
        auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(
            lwt - fs::file_time_type::clock::now() + std::chrono::system_clock::now());
        std::time_t t = std::chrono::system_clock::to_time_t(sctp);
        std::cout << "modified: " << std::ctime(&t);
    }
}

static void cmd_count(const std::string& path, const std::string& ext) {
    size_t count = 0;
    std::error_code ec;
    for (auto& e : fs::recursive_directory_iterator(path, ec)) {
        if (!e.is_regular_file()) continue;
        if (ext.empty() || e.path().extension() == ext) count++;
    }
    std::cout << count << " files";
    if (!ext.empty()) std::cout << " (" << ext << ")";
    std::cout << "\n";
}

static void cmd_lines(const std::string& path, const std::string& ext) {
    size_t total = 0, files = 0;
    std::error_code ec;
    for (auto& e : fs::recursive_directory_iterator(path, ec)) {
        if (!e.is_regular_file()) continue;
        if (!ext.empty() && e.path().extension() != ext) continue;
        std::ifstream f(e.path());
        std::string line;
        size_t n = 0;
        while (std::getline(f, line)) n++;
        total += n; files++;
    }
    std::cout << total << " lines in " << files << " files";
    if (!ext.empty()) std::cout << " (" << ext << ")";
    std::cout << "\n";
}

static void cmd_size(const std::string& path) {
    uintmax_t total = 0;
    std::error_code ec;
    for (auto& e : fs::recursive_directory_iterator(path, ec))
        if (e.is_regular_file()) total += e.file_size(ec);
    double mb = total / (1024.0 * 1024.0);
    std::cout << total << " bytes  (" << std::fixed << std::setprecision(2) << mb << " MB)\n";
}

static void cmd_find(const std::string& path, const std::string& pattern) {
    std::error_code ec;
    for (auto& e : fs::recursive_directory_iterator(path, ec)) {
        std::string name = e.path().filename().string();
        if (name.find(pattern) != std::string::npos)
            std::cout << e.path().string() << "\n";
    }
}

static void cmd_newer(const std::string& path, int seconds) {
    auto now = fs::file_time_type::clock::now();
    auto cutoff = now - std::chrono::seconds(seconds);
    std::error_code ec;
    for (auto& e : fs::recursive_directory_iterator(path, ec)) {
        if (!e.is_regular_file()) continue;
        auto lwt = e.last_write_time(ec);
        if (!ec && lwt >= cutoff)
            std::cout << e.path().string() << "\n";
    }
}

static void cmd_dupes(const std::string& path) {
    std::map<uintmax_t, std::vector<std::string>> by_size;
    std::error_code ec;
    for (auto& e : fs::recursive_directory_iterator(path, ec))
        if (e.is_regular_file())
            by_size[e.file_size(ec)].push_back(e.path().string());
    bool found = false;
    for (auto& [sz, paths] : by_size) {
        if (paths.size() > 1) {
            found = true;
            std::cout << "[" << sz << " bytes]\n";
            for (auto& p : paths) std::cout << "  " << p << "\n";
        }
    }
    if (!found) std::cout << "no duplicates found\n";
}

static void cmd_tree(const std::string& path, int max_depth, int depth = 0, const std::string& prefix = "") {
    if (depth > max_depth) return;
    std::error_code ec;
    std::vector<fs::directory_entry> entries;
    for (auto& e : fs::directory_iterator(path, ec)) entries.push_back(e);
    std::sort(entries.begin(), entries.end(), [](auto& a, auto& b){
        if (a.is_directory() != b.is_directory()) return a.is_directory() > b.is_directory();
        return a.path().filename() < b.path().filename();
    });
    for (size_t i = 0; i < entries.size(); i++) {
        bool last = (i == entries.size() - 1);
        std::cout << prefix << (last ? "└── " : "├── ") << entries[i].path().filename().string();
        if (entries[i].is_directory()) std::cout << "/";
        std::cout << "\n";
        if (entries[i].is_directory())
            cmd_tree(entries[i].path().string(), max_depth, depth+1, prefix + (last ? "    " : "│   "));
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) { print_usage(); return 1; }
    std::string cmd = argv[1];

    if (cmd == "stat" && argc >= 3) {
        cmd_stat(argv[2]);
    } else if (cmd == "hash" && argc >= 3) {
        std::cout << file_sha256(argv[2]) << "\n";
    } else if (cmd == "count" && argc >= 3) {
        cmd_count(argv[2], argc >= 4 ? argv[3] : "");
    } else if (cmd == "lines" && argc >= 3) {
        cmd_lines(argv[2], argc >= 4 ? argv[3] : "");
    } else if (cmd == "size" && argc >= 3) {
        cmd_size(argv[2]);
    } else if (cmd == "find" && argc >= 4) {
        cmd_find(argv[2], argv[3]);
    } else if (cmd == "newer" && argc >= 4) {
        cmd_newer(argv[2], std::stoi(argv[3]));
    } else if (cmd == "dupes" && argc >= 3) {
        cmd_dupes(argv[2]);
    } else if (cmd == "tree" && argc >= 3) {
        std::cout << argv[2] << "/\n";
        cmd_tree(argv[2], argc >= 4 ? std::stoi(argv[4]) : 3);
    } else {
        print_usage();
        return 1;
    }
    return 0;
}
