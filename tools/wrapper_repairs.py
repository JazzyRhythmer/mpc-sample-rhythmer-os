"""Repair decorated numeric enum readback without changing DSP or preset data."""
def repair(source):
    old='''        int idx = -1;
        if (isdigit((unsigned char)s[0])) idx = atoi(s);'''
    new='''        int idx = -1;
        /* Native enums can return labels such as 8', 1/16 or 16T.
         * Bare integers remain indices, preserving the published API. */
        if (strspn(s, "0123456789") != strlen(s))
            for (int i = 0; i < p->nopts; ++i)
                if (!strcasecmp(s, p->opts[i])) { idx = i; break; }
        if (idx >= 0) return p->nopts > 1 ? (float)idx / (p->nopts - 1) : 0;
        if (isdigit((unsigned char)s[0])) idx = atoi(s);'''
    assert old in source,'Review upstream enum parser before applying repair'
    return source.replace(old,new)
