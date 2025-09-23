import {
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import React from "react";
import { router } from "expo-router";

const Plans = () => {
  return (
    <View style={styles.container}>
      <View style={styles.logoAndSettingsTitle}>
        <TouchableOpacity onPress={() => router.back()}>
          <Image
            source={require("../../assets/images/back.png")}
            style={{ width: 35, height: 35, resizeMode: "contain" }}
          />
        </TouchableOpacity>
        <Text
          style={{
            fontFamily: "Poppins-SemiBold",
            fontSize: 20,
            color: "#000000ff",
            marginLeft: 60,
          }}
        >
          Upgrade Plan
        </Text>
      </View>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          flexDirection: "column",
          gap:25,
          justifyContent: "center",
          width: 320,
        }}
      >
        <View style={styles.subscriptionWrapper}>
            <View style={{width:"100%",justifyContent:"center",alignItems:"center"}}>
          <Text style={{ fontFamily: "Poppins-SemiBold", marginBottom: 10,marginTop:19 }}>
            Basic Explorer
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              marginBottom: 10,
              fontSize: 35,
            }}
          >
            Free
          </Text>
          </View>

          <View
            style={{
              borderBottomColor: "#d2d2d2ff",
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
            }}
          />
          <View style={{flexDirection:"column",gap:10,padding:25}}>
            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Access to personalized travel recommendations.
           </Text>
           </View>

            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Save limited destinations in your &quot;Saved List.&quot;
           </Text>
           </View>

            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Basic AI-generated trip itineraries.
           </Text>
           </View>

            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Ad-supported experience.
           </Text>
           </View>

           <View
            style={{
              borderBottomColor: "#d2d2d2ff",
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
              marginBottom:10,
            }}
          />

          <Text style={{textAlign:"center",fontFamily:"Poppins-Medium",color:"#b7b7b7ff"}}>
            Your current plan
          </Text>

          </View>
        </View>

        <View style={styles.subscriptionWrapper}>
          <View style={{position:"absolute",right:1,padding:4,backgroundColor:"rgba(231, 168, 9, 0.87)",borderTopRightRadius:10,borderBottomLeftRadius:10,}}>
           <Text style={{fontFamily:"Poppins-Regular",fontSize:10,color:"white"}}>
            Popular
           </Text>
          </View>
            <View style={{width:"100%",justifyContent:"center",alignItems:"center"}}>
          <Text style={{ fontFamily: "Poppins-SemiBold", marginBottom: 10,marginTop:19 }}>
            Premium Adventurer
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              marginBottom: 10,
              fontSize: 35,
            }}
          >
            EGP 499.99 <Text style={{fontSize:12}}>/ month</Text>
          </Text>
          </View>

          <View
            style={{
              borderBottomColor: "#d2d2d2ff",
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
            }}
          />
          <View style={{flexDirection:"column",gap:10,padding:25}}>
            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Ad-free experience.
           </Text>
           </View>

            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Enhanced AI-generated trip itineraries.
           </Text>
           </View>

            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Exclusive access to articles.
           </Text>
           </View>


           <View
            style={{
              borderBottomColor: "#d2d2d2ff",
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
              marginBottom:10,
            }}
          />

         <TouchableOpacity style={{backgroundColor:"#D4AF37",justifyContent:"center",alignItems:"center",padding:20,borderRadius:35,}} onPress={()=>{console.log("Plan Selected!")}}>
            <Text style={{fontFamily:"Poppins-SemiBold",color:"white"}}>
                Select Plan
            </Text>
         </TouchableOpacity>

          </View>
        </View>

         <View style={styles.subscriptionWrapper}>
            <View style={{width:"100%",justifyContent:"center",alignItems:"center"}}>
          <Text style={{ fontFamily: "Poppins-SemiBold", marginBottom: 10,marginTop:19 }}>
            Family Voyage
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              marginBottom: 10,
              fontSize: 35,
            }}
          >
            EGP 729.99 <Text style={{fontSize:12}}>/ month</Text>
          </Text>
          </View>

          <View
            style={{
              borderBottomColor: "#d2d2d2ff",
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
            }}
          />
          <View style={{flexDirection:"column",gap:10,padding:25}}>
            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            All Premium Adventurer benefits. 
           </Text>
           </View>

            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Family-friendly trip planning for up to 4 persons.
           </Text>
           </View>

          

            

           <View
            style={{
              borderBottomColor: "#d2d2d2ff",
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
              marginBottom:10,
            }}
          />

         <TouchableOpacity style={{backgroundColor:"#D4AF37",justifyContent:"center",alignItems:"center",padding:20,borderRadius:35}} onPress={()=>{console.log("Plan Selected!")}}>
            <Text style={{fontFamily:"Poppins-SemiBold",color:"white"}}>
                Select Plan
            </Text>
         </TouchableOpacity>

          </View>
        </View>

         <View style={styles.subscriptionWrapper}>
            <View style={{width:"100%",justifyContent:"center",alignItems:"center"}}>
          <Text style={{ fontFamily: "Poppins-SemiBold", marginBottom: 10,marginTop:19 }}>
            Wanderlust Pro
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              marginBottom: 10,
              fontSize: 35,
            }}
          >
            EGP 999.99 <Text style={{fontSize:12}}>/ month</Text>
          </Text>
          </View>

          <View
            style={{
              borderBottomColor: "#d2d2d2ff",
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
            }}
          />
          <View style={{flexDirection:"column",gap:10,padding:25}}>
            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            All Family Voyage benefits. 
           </Text>
           </View>

            {/* <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Access to premium travel content, including immersive VR experiences. 
           </Text>
           </View> */}

            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Access to AI-voice assistant.
           </Text>
           </View>

          

            

           <View
            style={{
              borderBottomColor: "#d2d2d2ff",
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
              marginBottom:10,
            }}
          />

         <TouchableOpacity style={{backgroundColor:"#D4AF37",justifyContent:"center",alignItems:"center",padding:20,borderRadius:35}} onPress={()=>{console.log("Plan Selected!")}}>
            <Text style={{fontFamily:"Poppins-SemiBold",color:"white"}}>
                Select Plan
            </Text>
         </TouchableOpacity>

          </View>
        </View>

        <View style={styles.subscriptionWrapper}>
            <View style={{width:"100%",justifyContent:"center",alignItems:"center"}}>
          <Text style={{ fontFamily: "Poppins-SemiBold", marginBottom: 10,marginTop:19 }}>
            Lifetime Explorer 
          </Text>

          <Text
            style={{
              fontFamily: "Poppins-SemiBold",
              marginBottom: 10,
              fontSize: 35,
            }}
          >
            EGP 14,999.99 
          </Text>
          </View>

          <View
            style={{
              borderBottomColor: "#d2d2d2ff",
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
            }}
          />
          <View style={{flexDirection:"column",gap:10,padding:25}}>
            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            All Wanderlust Pro benefits. 
           </Text>
           </View>

            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Lifetime access to Historai&apos;s premium features. 
           </Text>
           </View>

            <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
            Never worry about subscription renewals.
           </Text>
           </View>

             <View style={{flexDirection:"row",alignItems:'center',gap:10}}>
           <Image
           source={require("../../assets/images/check.png")}
           style={{width:15,height:15}}
           />

           <Text style={{fontFamily:"Poppins-Medium",fontSize:13}}>
           Priority access to beta features and enhancements.
           </Text>
           </View>

          

            

           <View
            style={{
              borderBottomColor: "#d2d2d2ff",
              borderBottomWidth: 1,
              width: "100%",
              height: 10,
              marginBottom:10,
            }}
          />

         <TouchableOpacity style={{backgroundColor:"#D4AF37",justifyContent:"center",alignItems:"center",padding:20,borderRadius:35}} onPress={()=>{console.log("Plan Selected!")}}>
            <Text style={{fontFamily:"Poppins-SemiBold",color:"white"}}>
                Select Plan
            </Text>
         </TouchableOpacity>

          </View>
        </View>
      </ScrollView>
    </View>
  );
};

export default Plans;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 70,
    paddingHorizontal: 30,
    flexDirection: "column",
    alignItems: "center",
  },
  logoAndSettingsTitle: {
    flexDirection: "row",
    width: "100%",
    marginBottom: 15,
  },
  subscriptionWrapper: {
    position:"relative",
    width: "100%",
    height: "auto",
    backgroundColor: "#e7e7e7ff",
    borderRadius: 10,
    borderWidth: 0.1,
  },
});
