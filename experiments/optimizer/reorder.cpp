#define main lp_oldmain
#include "lp.cpp"
#undef main
#include <cassert>
mt19937 rng(105);
double rr(){return double(rng())/rng.max();}
int main(int argc,char**argv){
 int M,R,Q;string s;cin>>M;getline(cin,s);for(int i=0;i<M;i++){getline(cin,s);int p=s.find(" -> ");prices[id(s.substr(p+4))]=stoi(s.substr(0,p));}cin>>R;getline(cin,s);vector<Reaction>rs;map<string,int>lookup;for(int i=0;i<R;i++){getline(cin,s);int p=s.find(" -> ");rs.push_back({side(s.substr(0,p)),side(s.substr(p+4)),s});lookup[s]=i;}cin>>Q;vector<pair<int,int>>qs;for(int i=0,n;i<Q;i++){string m;cin>>n>>m;qs.push_back({id(m),n});}int K=ids.size();ifstream src(argv[1]);vector<vector<int>>seqs(1);while(getline(src,s)){if(!s.empty()&&s.back()=='\r')s.pop_back();if(s.empty()){if(!seqs.back().empty())seqs.emplace_back();}else seqs.back().push_back(lookup.at(s));}if(seqs.back().empty())seqs.pop_back();assert(seqs.size()==qs.size());int trials=argc>2?atoi(argv[2]):1000;long long total=0;
 auto eval=[&](const vector<int>&seq,int t,int n){vector<int>inv(K);long long c=0;for(int j:seq){for(auto[m,k]:rs[j].a){if(inv[m]<k){if(prices[m]<0)return LLONG_MAX;int d=k-inv[m];c+=d*prices[m];inv[m]=k;}inv[m]-=k;}for(auto[m,k]:rs[j].b)inv[m]+=k;}return inv[t]>=n?c:LLONG_MAX;};
 for(int ca=0;ca<Q;ca++){
  auto[t,n]=qs[ca];auto best=seqs[ca];long long bst=eval(best,t,n);vector<int>base(R),allow(K);for(int j:best)base[j]++;for(int j=0;j<R;j++){for(auto[m,k]:rs[j].a)allow[m]+=base[j]*k;for(auto[m,k]:rs[j].b)allow[m]-=base[j]*k;}for(int &v:allow)v=max(0,v);
  for(int tr=0;tr<trials;tr++){
   vector<int>cnt=base,virt=allow,inv(K),seq;long long cost=0;bool fail=false;vector<double>prio(R);for(double&v:prio)v=rr();
   for(int step=0;step<(int)seqs[ca].size();step++){
    int at=-1;double bv=INF;bool needExtra=false;
    for(int pass=0;pass<2&&at<0;pass++)for(int j=0;j<R;j++)if(cnt[j]){
     bool ok=true;int deficit=0,actual=0;for(auto[m,k]:rs[j].a){if(virt[m]<k){if(pass==0||prices[m]<0){ok=false;break;}deficit+=(k-virt[m])*prices[m];}if(inv[m]<k&&prices[m]>=0)actual+=(k-inv[m])*prices[m];}if(!ok)continue;
     double noise[]={0,3,10,30,100,300,1000};double v=actual+rr()*noise[tr%7];if(tr%11==0)v=rr()*1000;if(tr%13==0)v=prio[j]*1000;if(pass)v+=deficit*1000;
     if(v<bv)bv=v,at=j,needExtra=pass;
    }
    if(at<0){fail=true;break;}
    for(auto[m,k]:rs[at].a){if(virt[m]<k)virt[m]=k;if(inv[m]<k){if(prices[m]<0){fail=true;break;}cost+=(k-inv[m])*prices[m];inv[m]=k;}virt[m]-=k;inv[m]-=k;}if(fail)break;for(auto[m,k]:rs[at].b)virt[m]+=k,inv[m]+=k;cnt[at]--;seq.push_back(at);
    if(cost>=bst)break;
    if(inv[t]>=n){if(cost<bst){bst=cost;best=seq;}break;}
   }
  }
  cerr<<"case"<<ca+1<<" cost"<<bst<<" steps"<<best.size()<<"\n";total+=bst;for(int j:best)cout<<rs[j].s<<"\n";cout<<"\n";
 }cerr<<"TOTAL "<<total<<"\n";
}
