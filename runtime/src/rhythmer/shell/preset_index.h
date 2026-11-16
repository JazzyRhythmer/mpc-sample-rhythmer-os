// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 jazzy rhythmer
#pragma once
#include <cstdint>
#include <cstddef>
namespace rhythmer {
// A relative preset turn wraps; absolute pot positions remain bounded by their bindings.
inline unsigned preset_index(int64_t position, size_t count) {
    if(!count)return 0;
    const auto n=int64_t(count);return unsigned((position%n+n)%n);
}
}
