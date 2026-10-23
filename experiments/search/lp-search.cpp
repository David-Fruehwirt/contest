#include <bits/stdc++.h>
using namespace std;
const double EPS=1e-8, INF=1e100;
struct LPSolver {
 int m,n;vector<int>B,N;vector<vector<double>>D;
 LPSolver(vector<vector<double>> A, vector<double>b,vector<double>c):m(b.size()),n(c.size()),N(n+1),B(m),D(m+2,vector<double>(n+2)){
 for(int i=0;i<m;i++)for(int j=0;j<n;j++)D[i][j]=A[i][j];
 for(int i=0;i<m;i++)B[i]=n+i,D[i][n]=-1,D[i][n+1]=b[i];
 for(int j=0;j<n;j++)N[j]=j,D[m][j]=-c[j];N[n]=-1;D[m+1][n]=1;}
 void pivot(int r,int s){double inv=1/D[r][s];for(int i=0;i<m+2;i++)if(i!=r)for(int j=0;j<n+2;j++)if(j!=s)D[i][j]-=D[r][j]*D[i][s]*inv;for(int j=0;j<n+2;j++)if(j!=s)D[r][j]*=inv;for(int i=0;i<m+2;i++)if(i!=r)D[i][s]*=-inv;D[r][s]=inv;swap(B[r],N[s]);}
 bool simplex(int phase){int x=phase==1?m+1:m;while(1){int s=-1;for(int j=0;j<=n;j++){if(phase==2&&N[j]==-1)continue;if(D[x][j]<-EPS&&(s==-1||N[j]<N[s]))s=j;}if(s==-1)return true;int r=-1;for(int i=0;i<m;i++)if(D[i][s]>EPS){if(r==-1)r=i;else{double a=D[i][n+1]/D[i][s],b=D[r][n+1]/D[r][s];if(a<b-EPS||(abs(a-b)<EPS&&B[i]<B[r]))r=i;}}if(r==-1)return false;pivot(r,s);}}
 double solve(vector<double>&x){int r=0;for(int i=1;i<m;i++)if(D[i][n+1]<D[r][n+1])r=i;if(D[r][n+1]<-EPS){pivot(r,n);if(!simplex(1)||D[m+1][n+1]<-EPS||abs(D[m+1][n+1])>EPS)return -INF;for(int i=0;i<m;i++)if(B[i]==-1){int s=0;for(int j=1;j<=n;j++)if(D[i][j]<D[i][s]-EPS||(abs(D[i][j]-D[i][s])<EPS&&N[j]<N[s]))s=j;pivot(i,s);}}
 if(!simplex(2))return INF;x.assign(n,0);for(int i=0;i<m;i++)if(B[i]<n)x[B[i]]=D[i][n+1];return D[m][n+1];}
};

struct R {vector<pair<int,int>> a,b;string s;};
vector<R> rr; vector<vector<int>> opts; vector<string> names; map<string,int> ids;
vector<int> price; vector<double> unit;
int id(string s){if(ids.count(s))return ids[s];int n=names.size();names.push_back(s);return ids[s]=n;}
vector<pair<int,int>> side(string s){vector<pair<int,int>> a; for(char &c:s)if(c==',')c=' ';istringstream t(s);int n;string m;while(t>>n>>m)a.push_back({id(m),n});return a;}
string line(){string s;do{if(!getline(cin,s))return "";if(s.size()&&s.back()=='\r')s.pop_back();}while(s.empty());return s;}
mt19937 rng(5871); double rnd(){return (rng()+.5)/4294967296.;}
struct Policy{vector<int> p;vector<double> order;};
vector<int> inv,actual,steps; int actualspent; vector<bool> active,used;int spent,cnt; bool collect;
bool makeq(const Policy &p,int m,int n){int need=n-inv[m];if(need<=0)return true;used[m]=1;int ri=p.p[m];if(ri==-1||active[m]){if(price[m]<0)return false;inv[m]+=need;spent+=need*price[m];return spent<100000000;}
 auto &r=rr[ri];int qty=0;for(auto [x,k]:r.b)if(x==m)qty=k;if(!qty)return false;int times=(need+qty-1)/qty;if(times>5000)return false;active[m]=1;
 vector<pair<int,int>> a=r.a;sort(a.begin(),a.end(),[&](auto x,auto y){return p.order[x.first]<p.order[y.first];});
 for(int i=0;i<times;i++){for(auto [x,k]:a){if(!makeq(p,x,k)){active[m]=0;return false;}inv[x]-=k;}for(auto [x,k]:r.b)inv[x]+=k;if(++cnt>8000){active[m]=0;return false;}for(auto [x,k]:r.a){int shortage=max(0,k-actual[x]);if(shortage){if(price[x]<0){active[m]=0;return false;}actualspent+=shortage*price[x];actual[x]+=shortage;}}for(auto [x,k]:r.a)actual[x]-=k;for(auto [x,k]:r.b)actual[x]+=k;if(collect)steps.push_back(ri);}
 active[m]=0;return inv[m]>=n;
}
int eval(const Policy &p,int m,int n,bool col=false){int z=names.size();inv.assign(z,0);actual.assign(z,0);actualspent=0;active.assign(z,0);used.assign(z,0);steps.clear();spent=cnt=0;collect=col;return makeq(p,m,n)&&actual[m]>=n?actualspent:1000000000;}
int main(int argc,char **argv){double seconds=argc>1?atof(argv[1]):2;int buys=stoi(line());vector<pair<int,int>> pp;for(int i=0;i<buys;i++){string s=line();auto k=s.find(" -> ");pp.push_back({id(s.substr(k+4)),stoi(s.substr(0,k))});}int nr=stoi(line());for(int i=0;i<nr;i++){string s=line();auto k=s.find(" -> ");rr.push_back({side(s.substr(0,k)),side(s.substr(k+4)),s});}int nc=stoi(line());vector<pair<int,int>> cases;for(int i=0;i<nc;i++){istringstream t(line());int n;string m;t>>n>>m;cases.push_back({id(m),n});}int z=names.size();price.assign(z,-1);opts.resize(z);unit.assign(z,1e12);Policy base;base.p.assign(z,-2);base.order.assign(z,0);for(auto [m,p]:pp){price[m]=p;unit[m]=p;base.p[m]=-1;opts[m].push_back(-1);}for(int i=0;i<nr;i++)for(auto [m,n]:rr[i].b)opts[m].push_back(i);
 for(int j=0;j<500;j++){bool ch=false;for(int i=0;i<nr;i++){double c=0;for(auto [x,k]:rr[i].a)c+=unit[x]*k;for(auto [m,k]:rr[i].b)if(c/k+1e-9<unit[m]){unit[m]=c/k;base.p[m]=i;ch=true;}}if(!ch)break;}
 vector<vector<double>> weights(z);for(int m=0;m<z;m++){for(int i:opts[m]){double c=price[m];if(i>=0){c=0;for(auto [x,k]:rr[i].a)c+=unit[x]*k;for(auto [x,k]:rr[i].b)if(x==m)c/=k;}weights[m].push_back(pow(1+c/max(.01,unit[m]),-2));}}
 vector<vector<double>> A(z,vector<double>(nr+z)); vector<double> objective(nr+z);for(int i=0;i<nr;i++){for(auto [m,k]:rr[i].a)A[m][i]+=k;for(auto [m,k]:rr[i].b)A[m][i]-=k;}for(int m=0;m<z;m++){if(price[m]>=0){A[m][nr+m]=-1;objective[nr+m]=-price[m];}else objective[nr+m]=-10000;} map<int,vector<double>> lpcache; map<int,Policy> warm;map<pair<int,int>,pair<int,vector<int>>> cache;
 for(int ci=0;ci<nc;ci++){auto [target,n]=cases[ci];if(cache.count({target,n})){auto &[s,ss]=cache[{target,n}];for(int ri:ss)cout<<rr[ri].s<<'\n';cout<<'\n';cerr<<ci+1<<" cached "<<s<<'\n';continue;}
  vector<double> lx;if(lpcache.count(target))lx=lpcache[target];else{vector<double>b(z);b[target]=-1;LPSolver lp(A,b,objective);lp.solve(lx);lpcache[target]=lx;}vector<vector<double>> lpweights=weights;Policy lpbase=base;for(int m=0;m<z;m++){double top=0;for(int j=0;j<(int)opts[m].size();j++){int ri=opts[m][j];double v=ri<0?lx[nr+m]:lx[ri];if(ri>=0)for(auto [x,k]:rr[ri].b)if(x==m)v*=k;lpweights[m][j]=max(0.,v)+.00001*weights[m][j];if(v>top){top=v;lpbase.p[m]=ri;}}}Policy best=base;if(eval(lpbase,target,n)<eval(best,target,n))best=lpbase;for(int trial=0;trial<100;trial++){Policy candidate=lpbase;for(int m=0;m<z;m++)if(opts[m].size()>1){discrete_distribution<int>d(lpweights[m].begin(),lpweights[m].end());candidate.p[m]=opts[m][d(rng)];candidate.order[m]=rnd();}if(eval(candidate,target,n)<eval(best,target,n))best=candidate;}if(warm.count(target)&&eval(warm[target],target,n)<eval(best,target,n))best=warm[target];int bs=eval(best,target,n),orig=bs;Policy cur=best;int cs=bs;vector<int> muts;auto refresh=[&](){eval(cur,target,n);muts.clear();for(int m=0;m<z;m++)if(used[m]&&opts[m].size()>1)muts.push_back(m);};refresh();auto start=chrono::steady_clock::now();int iter=0;
  while(!muts.empty()){double elapsed=chrono::duration<double>(chrono::steady_clock::now()-start).count();if(elapsed>seconds)break;iter++;Policy p=cur;int count=iter%9?rng()%3+1:rng()%8+2;for(int j=0;j<count;j++){int m=muts[rng()%muts.size()];if(rng()%6==0)p.p[m]=opts[m][rng()%opts[m].size()];else{auto &w=(rng()%3)?lpweights[m]:weights[m];discrete_distribution<int> d(w.begin(),w.end());p.p[m]=opts[m][d(rng)];}}
   if(iter%4==0)for(int j=0;j<8;j++)p.order[rng()%z]=rnd();int s=eval(p,target,n);double phase=fmod(elapsed/max(.1,seconds/5),1.);double temp=max(1.,bs*.015*pow(1-phase,3));
   if(s<cs||(s<1e8&&rnd()<exp((cs-s)/temp))){cur=move(p);cs=s;if(s<bs){best=cur;bs=s;}if(iter%4==0||s<bs)refresh();}
   if(iter%1500==0){cur=best;cs=bs;refresh();}
  }
  eval(best,target,n,true);cache[{target,n}]={bs,steps};warm[target]=best;for(int ri:steps)cout<<rr[ri].s<<'\n';cout<<'\n';cerr<<ci+1<<" "<<orig<<" -> "<<bs<<" it "<<iter<<'\n';
 }
}
