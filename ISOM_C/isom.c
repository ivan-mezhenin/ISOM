#include "isom.h"
#include <ctype.h>

void copy_str(char* d, const char* s) {
    strncpy(d, s, MAX_NAME - 1);
    d[MAX_NAME - 1] = '\0';
}

bool is_var(const char* s) {
    return s && s[0] == 'x';
}

// --- Parsing ---
Hypergraph* parse_hg(const char* str) {
    Hypergraph* g = (Hypergraph*)calloc(1, sizeof(Hypergraph));
    const char* p = str;
    
    while (*p && g->edge_cnt < MAX_EDGES) {
        while (*p == ' ') p++;
        const char* pred_start = p;
        while (*p && *p != '(') p++;
        if (!*p) break;
        
        Hyperedge* e = &g->edges[g->edge_cnt];
        int plen = p - pred_start;
        if (plen >= MAX_NAME) plen = MAX_NAME - 1;
        strncpy(e->pred, pred_start, plen);
        e->pred[plen] = '\0';
        
        p++;
        const char* args_start = p;
        while (*p && *p != ')') p++;
        if (*p != ')') { free(g); return NULL; }
        
        char args_str[1024] = {0};
        strncpy(args_str, args_start, p - args_start);
        
        e->arity = 0;
        char* tok = strtok(args_str, ",");
        while (tok && e->arity < MAX_ARGS) {
            copy_str(e->args[e->arity], tok);
            e->arity++;
            tok = strtok(NULL, ",");
        }
        
        if (g->edge_cnt == 0) g->arity = e->arity;
        g->edge_cnt++;
        p++;
        
        while (*p == ' ') p++;
        if (*p == '&') p++;
        else break;
    }
    return g;
}

void free_hg(Hypergraph* g) { if (g) free(g); }

void print_hg(Hypergraph* g) {
    if (!g) return;
    for (int i = 0; i < g->edge_cnt; i++) {
        Hyperedge* e = &g->edges[i];
        printf("%s(", e->pred);
        for (int j = 0; j < e->arity; j++) {
            printf("%s", e->args[j]);
            if (j < e->arity - 1) printf(",");
        }
        printf(") ");
    }
    printf("\n");
}

// --- Characteristics ---
typedef struct {
    char name[MAX_NAME];
    int vec[MAX_ARGS];
} ArgChar;

typedef struct {
    ArgChar* items;
    int count;
    int arity;
} GraphChar;

GraphChar* calc_char(Hypergraph* g) {
    char uniq[MAX_ARGS][MAX_NAME] = {{0}};
    int ucnt = 0;
    
    for (int i = 0; i < g->edge_cnt; i++)
        for (int j = 0; j < g->edges[i].arity; j++) {
            bool found = false;
            for (int k = 0; k < ucnt; k++)
                if (strcmp(uniq[k], g->edges[i].args[j]) == 0) { found = true; break; }
            if (!found && ucnt < MAX_ARGS) copy_str(uniq[ucnt++], g->edges[i].args[j]);
        }
    
    GraphChar* gc = (GraphChar*)malloc(sizeof(GraphChar));
    gc->count = ucnt;
    gc->arity = g->arity;
    gc->items = (ArgChar*)calloc(ucnt, sizeof(ArgChar));
    
    for (int i = 0; i < ucnt; i++) {
        copy_str(gc->items[i].name, uniq[i]);
        for (int j = 0; j < g->arity; j++) gc->items[i].vec[j] = 0;
        for (int e = 0; e < g->edge_cnt; e++)
            for (int a = 0; a < g->edges[e].arity; a++)
                if (strcmp(g->edges[e].args[a], uniq[i]) == 0)
                    gc->items[i].vec[a]++;
    }
    return gc;
}

void free_char(GraphChar* gc) {
    if (gc) { if (gc->items) free(gc->items); free(gc); }
}

int cmp_argchar(const void* a, const void* b) {
    ArgChar* ac1 = (ArgChar*)a;
    ArgChar* ac2 = (ArgChar*)b;
    for (int i = 0; i < MAX_ARGS; i++) {
        if (ac1->vec[i] < ac2->vec[i]) return -1;
        if (ac1->vec[i] > ac2->vec[i]) return 1;
    }
    return strcmp(ac1->name, ac2->name);
}

void sort_char(GraphChar* gc) {
    qsort(gc->items, gc->count, sizeof(ArgChar), cmp_argchar);
}

bool cmp_chars(GraphChar* c1, GraphChar* c2) {
    if (c1->count != c2->count || c1->arity != c2->arity) return false;
    sort_char(c1);
    sort_char(c2);
    for (int i = 0; i < c1->count; i++)
        for (int j = 0; j < c1->arity; j++)
            if (c1->items[i].vec[j] != c2->items[i].vec[j]) return false;
    return true;
}

// --- Unifiers ---
int get_constants(Hypergraph* g, char res[][MAX_NAME]) {
    int cnt = 0;
    for (int i = 0; i < g->edge_cnt; i++)
        for (int j = 0; j < g->edges[i].arity; j++)
            if (!is_var(g->edges[i].args[j])) {
                bool found = false;
                for (int k = 0; k < cnt; k++)
                    if (strcmp(res[k], g->edges[i].args[j]) == 0) { found = true; break; }
                if (!found && cnt < MAX_ARGS) copy_str(res[cnt++], g->edges[i].args[j]);
            }
    return cnt;
}

int get_variables(Hypergraph* g, char res[][MAX_NAME]) {
    int cnt = 0;
    for (int i = 0; i < g->edge_cnt; i++)
        for (int j = 0; j < g->edges[i].arity; j++)
            if (is_var(g->edges[i].args[j])) {
                bool found = false;
                for (int k = 0; k < cnt; k++)
                    if (strcmp(res[k], g->edges[i].args[j]) == 0) { found = true; break; }
                if (!found && cnt < MAX_ARGS) copy_str(res[cnt++], g->edges[i].args[j]);
            }
    return cnt;
}

