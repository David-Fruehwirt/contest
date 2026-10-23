#include <bits/stdc++.h>
using namespace std;
using VI=vector<int>;using P=pair<int,int>;using VP=vector<P>;
map<string,int> ids;vector<string> names;
int id(string s){if(!ids.count(s)){ids[s]=ids.size();names.push_back(s);}return ids[s];}
VP side(string s){VP a;stringstream ss(s);string z;while(getline(ss,z,',')){stringstream t(z);int k;string m;t>>k>>m;a.push_back({id(m),k});}return a;}
struct R{VP a,b;string s;};vector<R> rs;VI price;
int evaluate(VI seq,P target){VI inv(names.size());int cost=0;for(int j:seq){for(auto[m,k]:rs[j].a){int n=max(0,k-inv[m]);if(n&&price[m]<0)return INT_MAX;cost+=n*max(0,price[m]);inv[m]+=n;inv[m]-=k;}for(auto[m,k]:rs[j].b)inv[m]+=k;}return inv[target.first]>=target.second?cost:INT_MAX;}
int main(int argc,char**argv){ifstream in(argv[1]);int n;string s;in>>n;getline(in,s);map<int,int> pp;for(int i=0;i<n;i++){getline(in,s);int j=s.find(" -> ");pp[id(s.substr(j+4))]=stoi(s.substr(0,j));}in>>n;getline(in,s);map<string,int> ri;for(int i=0;i<n;i++){getline(in,s);int j=s.find(" -> ");ri[s]=i;rs.push_back({side(s.substr(0,j)),side(s.substr(j+4)),s});}in>>n;vector<P> ts;for(int i=0;i<n;i++){int k;in>>k>>s;ts.push_back({id(s),k});}price.assign(names.size(),-1);for(auto[m,k]:pp)price[m]=k;
ifstream src(argv[2]);vector<VI> cases;VI q;while(getline(src,s)){if(s.size()&&s.back()=='\r')s.pop_back();if(s.empty()){if(q.size()){cases.push_back(q);q.clear();}}else{if(!ri.count(s)){cerr<<"unknown";return 1;}q.push_back(ri[s]);}}if(q.size())cases.push_back(q);
ofstream out(argv[3]);mt19937 rng(923);double total=0,orig=0;auto start=chrono::steady_clock::now();double seconds=argc>4?stod(argv[4]):30;
for(int c=0;c<n;c++){VI best=cases[c];int bc=evaluate(best,ts[c]);orig+=bc;int trials=0;double end=seconds*(c+1)/n;
while(chrono::duration<double>(chrono::steady_clock::now()-start).count()<end){trials++;VI rem(rs.size()),inv(names.size()),produces(names.size());for(int j:cases[c])rem[j]++;for(int j=0;j<rs.size();j++)for(auto[m,k]:rs[j].b)produces[m]+=k*rem[j];VI seq;int cost=0;vector<double> noise(rs.size());double strength=pow(10.,uniform_real_distribution<double>(-2,2)(rng));for(auto&x:noise)x=uniform_real_distribution<double>(0,1)(rng)*strength;
while(seq.size()<cases[c].size()){int bj=-1;double bv=1e100;for(int j=0;j<rs.size();j++)if(rem[j]){bool ok=true;double val=noise[j];for(auto[m,k]:rs[j].a){int d=max(0,k-inv[m]);if(d&&price[m]<0){ok=false;break;}if(d){double w=price[m];if(produces[m])w*=1+strength;val+=d*w;}}if(ok&&val<bv){bv=val;bj=j;}}if(bj<0)break;seq.push_back(bj);rem[bj]--;for(auto[m,k]:rs[bj].a){int d=max(0,k-inv[m]);cost+=d*max(0,price[m]);inv[m]+=d-k;}for(auto[m,k]:rs[bj].b){inv[m]+=k;produces[m]-=k;}}
if(seq.size()==cases[c].size()&&cost<bc&&inv[ts[c].first]>=ts[c].second){bc=cost;best=seq;}}
total+=bc;cerr<<"case "<<c+1<<" "<<evaluate(cases[c],ts[c])<<" -> "<<bc<<" trials="<<trials<<"\n";if(c)out<<"\n";for(int j:best)out<<rs[j].s<<"\n";}
cerr<<"TOTAL "<<orig<<" -> "<<total<<"\n";
}
