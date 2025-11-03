#include <nlohmann/json.hpp>


int main(int argc, char** argv) {
    (void)(argc);
    (void)(argv);
    nlohmann::json j;
    j["key"] = "value";
    return 0;
}
